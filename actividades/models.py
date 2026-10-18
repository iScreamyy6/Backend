from django.db import models
from django.contrib.auth.models import User
from organizacion.models import Funcionario, Delegacion


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


class TipoAtencion(models.Model):
    id_tipo = models.AutoField(primary_key=True)
    codigo = models.CharField(max_length=20, unique=True, verbose_name='Código')
    nombre = models.CharField(max_length=150, unique=True, verbose_name='Nombre')
    descripcion = models.TextField(blank=True, verbose_name='Descripción')
    estado = models.CharField(
        max_length=20,
        choices=[('Activo', 'Activo'), ('Inactivo', 'Inactivo')],
        default='Activo'
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'tipos_atencion'
        verbose_name = 'Tipo de Atención'
        verbose_name_plural = 'Tipos de Atención'
        ordering = ['nombre']

    @property
    def id(self):
        return self.pk

    def __str__(self):
        return f"[{self.codigo}] {self.nombre}"


class SubAtencion(models.Model):
    id_subatencion = models.AutoField(primary_key=True)
    codigo = models.CharField(max_length=20, unique=True, verbose_name='Código')
    id_tipo = models.ForeignKey(
        TipoAtencion,
        on_delete=models.RESTRICT,
        db_column='id_tipo',
        related_name='subatenciones',
        verbose_name='Tipo de Atención'
    )
    nombre = models.CharField(max_length=150, verbose_name='Nombre')
    estado = models.CharField(
        max_length=20,
        choices=[('Activo', 'Activo'), ('Inactivo', 'Inactivo')],
        default='Activo'
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'sub_atenciones'
        verbose_name = 'Sub Atención'
        verbose_name_plural = 'Sub Atenciones'
        ordering = ['id_tipo__nombre', 'nombre']
        unique_together = ('id_tipo', 'nombre')

    @property
    def id(self):
        return self.pk

    @property
    def tipo(self):
        return self.id_tipo

    def __str__(self):
        return f"{self.nombre} ({self.id_tipo.nombre})"


class AtencionCiudadana(models.Model):
    id_atencion = models.AutoField(primary_key=True)
    folio = models.CharField(max_length=30, unique=True, verbose_name='Folio')
    solicitante = models.CharField(max_length=200, verbose_name='Solicitante')
    rut_solicitante = models.CharField(max_length=20, blank=True, null=True, verbose_name='RUT')
    telefono = models.CharField(max_length=30, blank=True, null=True, verbose_name='Teléfono')
    correo = models.EmailField(blank=True, null=True, verbose_name='Correo')
    direccion = models.CharField(max_length=250, blank=True, null=True, verbose_name='Dirección')
    id_tipo = models.ForeignKey(
        TipoAtencion,
        on_delete=models.RESTRICT,
        db_column='id_tipo',
        related_name='atenciones',
        verbose_name='Tipo de Atención'
    )
    id_subatencion = models.ForeignKey(
        SubAtencion,
        on_delete=models.RESTRICT,
        db_column='id_subatencion',
        related_name='atenciones',
        verbose_name='Sub Atención'
    )
    descripcion = models.TextField(verbose_name='Descripción del Requerimiento')
    id_delegacion = models.ForeignKey(
        Delegacion,
        on_delete=models.RESTRICT,
        db_column='id_delegacion',
        related_name='atenciones_ciudadanas',
        verbose_name='Delegación'
    )
    id_usuario_responsable = models.ForeignKey(
        User,
        on_delete=models.RESTRICT,
        db_column='id_usuario',
        related_name='atenciones_ingresadas',
        verbose_name='Usuario Responsable'
    )
    fecha_registro = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Registro')
    estado = models.CharField(
        max_length=30,
        choices=[
            ('Ingresada', 'Ingresada'),
            ('En Tramite', 'En Trámite'),
            ('Derivada', 'Derivada'),
            ('Resuelta', 'Resuelta'),
            ('Cerrada', 'Cerrada'),
        ],
        default='Ingresada'
    )

    class Meta:
        db_table = 'atenciones_ciudadanas'
        verbose_name = 'Atención Ciudadana'
        verbose_name_plural = 'Atenciones Ciudadanas'
        ordering = ['-fecha_registro']

    @property
    def id(self):
        return self.pk

    @property
    def tipo(self):
        return self.id_tipo

    @property
    def subatencion(self):
        return self.id_subatencion

    @property
    def delegacion(self):
        return self.id_delegacion

    @property
    def usuario_responsable(self):
        return self.id_usuario_responsable

    def save(self, *args, **kwargs):
        if not self.folio:
            super().save(*args, **kwargs)
            self.folio = f"ATC-{self.pk:05d}"
            return super().save(update_fields=['folio'])
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.folio or f'ATC-{self.pk}'} - {self.solicitante}"
