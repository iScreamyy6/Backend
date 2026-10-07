from django.db import models


class Actividad(models.Model):
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
    contacto = models.CharField(max_length=200, blank=True)
    telefono = models.CharField(max_length=20, blank=True)
    ingreso_tubo = models.BooleanField(default=False, verbose_name='Ingreso a Tubo')
    codigo_evidencia = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
        null=True,
        verbose_name='Código de Evidencia'
    )
    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Actividad'
        verbose_name_plural = 'Actividades'
        ordering = ['-fecha']

    def __str__(self):
        return f"{self.fecha} - {self.solicitud[:50]}"


class Evidencia(models.Model):
    actividad = models.ForeignKey(
        Actividad,
        on_delete=models.CASCADE,
        related_name='evidencias'
    )
    codigo = models.CharField(max_length=20, unique=True)
    archivo = models.FileField(upload_to='evidencias/', blank=True, null=True)
    imagen_verificada = models.BooleanField(default=False)
    verificador_valido = models.IntegerField(default=0)
    resultado = models.IntegerField(default=0)
    estado_validacion = models.CharField(
        max_length=30,
        choices=[
            ('Pendiente', 'Pendiente'),
            ('Aprobada', 'Aprobada'),
            ('Rechazada', 'Rechazada'),
            ('Corregir', 'Requiere Corrección'),
        ],
        default='Pendiente'
    )
    observacion = models.TextField(blank=True)
    fecha_carga = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Evidencia'
        verbose_name_plural = 'Evidencias'
        ordering = ['-fecha_carga']

    def __str__(self):
        return f"Evidencia {self.codigo}"

    @property
    def actividad_solicitud(self):
        return self.actividad.solicitud if self.actividad else ''

    @property
    def actividad_resumen(self):
        return self.actividad.accion if self.actividad else ''

    @property
    def responsable(self):
        return self.actividad.responsable if self.actividad else ''

    @property
    def item_evaluacion(self):
        return self.actividad.item_evaluacion if self.actividad else ''

    @property
    def fecha(self):
        return self.actividad.fecha.strftime('%d/%m/%Y') if self.actividad and self.actividad.fecha else ''

    @property
    def contacto(self):
        return self.actividad.contacto if self.actividad else ''

    @property
    def telefono(self):
        return self.actividad.telefono if self.actividad else ''

    @property
    def archivo_nombre(self):
        return f"{self.codigo.lower()}.jpg"

    @property
    def estado(self):
        return self.estado_validacion

    @property
    def observaciones(self):
        return self.observacion

