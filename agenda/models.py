from django.db import models
from django.contrib.auth.models import User
from organizacion.models import Delegacion, Funcionario


class Compromiso(models.Model):
    id_compromiso = models.AutoField(primary_key=True)
    codigo = models.CharField(
        max_length=30,
        unique=True,
        blank=True,
        null=True,
        verbose_name='Código de Compromiso'
    )
    usuario_creador = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='compromisos_creados',
        verbose_name='Usuario Creador'
    )
    id_delegacion = models.ForeignKey(
        Delegacion,
        on_delete=models.RESTRICT,
        db_column='id_delegacion',
        related_name='compromisos'
    )
    id_responsable = models.ForeignKey(
        Funcionario,
        on_delete=models.SET_NULL,
        db_column='id_responsable',
        related_name='compromisos',
        null=True,
        blank=True
    )
    id_actividad = models.ForeignKey(
        'actividades.Actividad',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='id_actividad',
        related_name='compromisos_tubo',
        verbose_name='Gestión de Origen'
    )
    fecha_solicitud = models.DateField()
    actividad = models.TextField(verbose_name='Actividad / Solicitud / Problema')
    tipo = models.CharField(
        max_length=10,
        choices=[('INT', 'Interno'), ('EXT', 'Externo')],
        default='EXT'
    )
    solicitante = models.CharField(max_length=200)
    territorio = models.CharField(max_length=200, blank=True, null=True)
    responsable = models.CharField(max_length=200)
    fecha_compromiso = models.DateField(null=True, blank=True, verbose_name='Fecha Comprometida')
    area_apoyo = models.CharField(max_length=200, blank=True, null=True, verbose_name='Área / Persona Apoyo')
    observaciones = models.TextField(blank=True, null=True, verbose_name='Avance / Observaciones')
    estado = models.CharField(
        max_length=20,
        choices=[
            ('INGRESADO', 'Ingresado'),
            ('PENDIENTE', 'Pendiente'),
            ('EN PROCESO', 'En Proceso'),
            ('REALIZADO', 'Realizado'),
        ],
        default='INGRESADO'
    )
    unidad = models.IntegerField(default=1)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'compromisos_tubo'
        verbose_name = 'Compromiso'
        verbose_name_plural = 'Compromisos'
        ordering = ['-fecha_solicitud']

    def save(self, *args, **kwargs):
        if not self.codigo:
            kwargs.pop('force_insert', None)
            super().save(*args, **kwargs)
            self.codigo = f"TUB-{self.pk:05d}"
            super().save(update_fields=['codigo'])
        else:
            super().save(*args, **kwargs)
        self._sincronizar_actividad()

    def _sincronizar_actividad(self):
        if not self.pk or getattr(self, '_skip_sync_actividad', False):
            return
        try:
            from actividades.models import Actividad
            act = self.id_actividad or Actividad.objects.filter(id_compromiso=self).first()
            if act:
                if not self.id_actividad_id:
                    self.id_actividad = act
                    Compromiso.objects.filter(pk=self.pk).update(id_actividad=act)
                if act.id_compromiso_id != self.pk:
                    Actividad.objects.filter(pk=act.pk).update(id_compromiso=self)

                mapa_estados = {
                    'REALIZADO': 'Realizado',
                    'EN PROCESO': 'En Proceso',
                    'PENDIENTE': 'Pendiente',
                    'INGRESADO': 'Pendiente',
                }
                nuevo_estado = mapa_estados.get((self.estado or '').upper(), 'Pendiente')
                if act.estado != nuevo_estado:
                    act.estado = nuevo_estado
                    Actividad.objects.filter(pk=act.pk).update(estado=nuevo_estado)
        except Exception:
            pass

    def __str__(self):
        cod = f"[{self.codigo}] " if self.codigo else ""
        return f"{cod}{self.actividad[:50]} - {self.estado}"

    @property
    def id(self):
        return self.pk

    # Alias para templates
    @property
    def delegacion(self):
        return self.id_delegacion
