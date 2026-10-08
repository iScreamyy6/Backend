from django.db import models
from organizacion.models import Funcionario


class Actividad(models.Model):
    id_actividad = models.AutoField(primary_key=True)
    id_funcionario = models.ForeignKey(
        Funcionario,
        on_delete=models.RESTRICT,
        db_column='id_funcionario',
        related_name='actividades'
    )
    fecha = models.DateField()
    solicitud = models.TextField(verbose_name='Solicitud / Problema')
    accion = models.CharField(max_length=300, verbose_name='Acción Realizada')
    responsable = models.CharField(max_length=200)
    item_evaluacion = models.CharField(max_length=200, verbose_name='Ítem de Evaluación')
    estado = models.CharField(
        max_length=30,
        choices=[
            ('Pendiente', 'Pendiente'),
            ('En Proceso', 'En Proceso'),
            ('Realizado', 'Realizado'),
        ],
        default='Pendiente'
    )
    contacto = models.CharField(max_length=200, blank=True, null=True)
    telefono = models.CharField(max_length=30, blank=True, null=True)
    ingreso_tubo = models.BooleanField(default=False, verbose_name='Ingreso a Tubo')
    codigo_evidencia = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        null=True,
        verbose_name='Código de Evidencia'
    )
    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'actividades'
        verbose_name = 'Actividad'
        verbose_name_plural = 'Actividades'
        ordering = ['-fecha']

    def __str__(self):
        return f"{self.fecha} - {self.solicitud[:50]}"

    @property
    def id(self):
        return self.pk

    # Alias para templates
    @property
    def funcionario(self):
        return self.id_funcionario


class Evidencia(models.Model):
    id_evidencia = models.AutoField(primary_key=True)
    id_actividad = models.ForeignKey(
        Actividad,
        on_delete=models.CASCADE,
        db_column='id_actividad',
        related_name='evidencias'
    )
    codigo = models.CharField(max_length=50, unique=True)
    archivo_ruta = models.CharField(max_length=255, verbose_name='Ruta / Nombre Archivo')
    imagen_verificada = models.BooleanField(default=False)
    verificador_valido = models.BooleanField(default=False)
    resultado = models.IntegerField(default=0)
    estado_validacion = models.CharField(
        max_length=20,
        choices=[
            ('Pendiente', 'Pendiente'),
            ('Aprobada', 'Aprobada'),
            ('Rechazada', 'Rechazada'),
            ('Corregir', 'Requiere Corrección'),
        ],
        default='Pendiente'
    )
    observacion = models.TextField(blank=True, null=True)
    fecha_carga = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'evidencias'
        verbose_name = 'Evidencia'
        verbose_name_plural = 'Evidencias'
        ordering = ['-fecha_carga']

    def __str__(self):
        return f"Evidencia {self.codigo}"

    @property
    def id(self):
        return self.pk

    # Alias para compatibilidad con templates
    @property
    def actividad(self):
        return self.id_actividad

    @property
    def actividad_solicitud(self):
        return self.id_actividad.solicitud if self.id_actividad else ''

    @property
    def actividad_resumen(self):
        return self.id_actividad.accion if self.id_actividad else ''

    @property
    def fecha(self):
        return self.id_actividad.fecha.strftime('%d/%m/%Y') if self.id_actividad and self.id_actividad.fecha else ''

    @property
    def archivo_nombre(self):
        return self.archivo_ruta

    @property
    def estado(self):
        return self.estado_validacion

    @property
    def observaciones(self):
        return self.observacion
