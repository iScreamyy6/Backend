from django.db import models
from organizacion.models import Delegacion, Funcionario


class Compromiso(models.Model):
    id_compromiso = models.AutoField(primary_key=True)
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

    def __str__(self):
        return f"{self.actividad[:50]} - {self.estado}"

    @property
    def id(self):
        return self.pk

    # Alias para templates
    @property
    def delegacion(self):
        return self.id_delegacion
