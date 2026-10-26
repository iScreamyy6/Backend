from django.db import models
from django.contrib.auth.models import User
from organizacion.models import Funcionario, Delegacion


class Actividad(models.Model):
    id_actividad = models.AutoField(primary_key=True)
    codigo = models.CharField(
        max_length=30,
        unique=True,
        blank=True,
        null=True,
        verbose_name='Código de Gestión'
    )
    usuario_creador = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='actividades_creadas',
        verbose_name='Usuario Creador'
    )
    id_funcionario = models.ForeignKey(
        Funcionario,
        on_delete=models.RESTRICT,
        db_column='id_funcionario',
        related_name='actividades'
    )
    id_delegacion = models.ForeignKey(
        Delegacion,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='id_delegacion',
        related_name='actividades_delegacion',
        verbose_name='Delegación'
    )
    fecha = models.DateField()

    # Solicitante / Vecino (unificado)
    solicitante = models.CharField(max_length=200, blank=True, null=True, verbose_name='Solicitante / Vecino')
    rut_solicitante = models.CharField(max_length=20, blank=True, null=True, verbose_name='RUT')
    telefono = models.CharField(max_length=30, blank=True, null=True, verbose_name='Teléfono')
    correo = models.EmailField(blank=True, null=True, verbose_name='Correo Electrónico')
    direccion = models.CharField(max_length=250, blank=True, null=True, verbose_name='Dirección / Sector')
    territorio = models.CharField(max_length=200, blank=True, null=True, verbose_name='Territorio / Sector')
    contacto = models.CharField(max_length=200, blank=True, null=True)

    # Clasificación en catálogo
    id_tipo = models.ForeignKey(
        'TipoAtencion',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='id_tipo',
        related_name='actividades_clasificadas',
        verbose_name='Tipo de Atención'
    )
    id_subatencion = models.ForeignKey(
        'SubAtencion',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='id_subatencion',
        related_name='actividades_clasificadas',
        verbose_name='Sub Atención'
    )

    # Requerimiento y acción
    solicitud = models.TextField(verbose_name='Solicitud / Problema / Requerimiento')
    accion = models.CharField(max_length=300, verbose_name='Acción Realizada')
    responsable = models.CharField(max_length=200)
    item_evaluacion = models.CharField(max_length=200, verbose_name='Ítem de Evaluación')

    # Derivación a Tubo de Trabajo y Enlaces
    ingreso_tubo = models.BooleanField(default=False, verbose_name='¿Derivado a Tubo de Trabajo?')
    id_compromiso = models.ForeignKey(
        'agenda.Compromiso',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='id_compromiso',
        related_name='gestion_origen',
        verbose_name='Compromiso en Tubo'
    )
    id_atencion = models.ForeignKey(
        'AtencionCiudadana',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='id_atencion',
        related_name='actividades_vinculadas',
        verbose_name='Atención Ciudadana de Origen'
    )
    id_gestion_social = models.ForeignKey(
        'GestionSocial',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='id_gestion_social',
        related_name='actividades_vinculadas',
        verbose_name='Gestión Social de Origen'
    )
    fecha_limite_tubo = models.DateField(null=True, blank=True, verbose_name='Fecha Límite Tubo')
    area_apoyo_tubo = models.CharField(max_length=200, blank=True, null=True, verbose_name='Área de Apoyo Tubo')

    # Especialización para Gestor Social
    es_gestion_social = models.BooleanField(default=False, verbose_name='¿Es Gestión Social?')
    requiere_visita = models.BooleanField(default=False, verbose_name='¿Requiere Visita en Terreno?')
    fecha_programada_visita = models.DateField(blank=True, null=True, verbose_name='Fecha Programada Visita')
    observaciones_sociales = models.TextField(blank=True, null=True, verbose_name='Observaciones / Diagnóstico Social')
    primera_gestion = models.CharField(max_length=200, blank=True, null=True, verbose_name='1ª Gestión Social')
    segunda_gestion = models.CharField(max_length=200, blank=True, null=True, verbose_name='2ª Gestión Social')
    fecha_visita = models.DateField(blank=True, null=True, verbose_name='Fecha Visita Realizada')
    fecha_entrega_informe = models.DateField(blank=True, null=True, verbose_name='Fecha Entrega Informe')
    tercera_gestion = models.CharField(max_length=200, blank=True, null=True, verbose_name='3ª Gestión Social')
    fecha_entrega_beneficio = models.DateField(blank=True, null=True, verbose_name='Fecha Entrega Beneficio')

    # Estado y verificación
    estado = models.CharField(
        max_length=30,
        choices=[
            ('Pendiente', 'Pendiente'),
            ('En Proceso', 'En Proceso'),
            ('Realizado', 'Realizado'),
        ],
        default='Pendiente'
    )
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
        verbose_name = 'Actividad / Gestión'
        verbose_name_plural = 'Actividades y Gestiones'
        ordering = ['-fecha', '-id_actividad']

    def save(self, *args, **kwargs):
        if not self.contacto and self.solicitante:
            self.contacto = self.solicitante
        elif not self.solicitante and self.contacto:
            self.solicitante = self.contacto

        if not self.codigo or not self.codigo_evidencia:
            kwargs.pop('force_insert', None)
            super().save(*args, **kwargs)
            updates = []
            if not self.codigo:
                prefijo = "SOC" if self.es_gestion_social else "GES"
                self.codigo = f"{prefijo}-{self.pk:05d}"
                updates.append('codigo')
            if not self.codigo_evidencia:
                if isinstance(self.fecha, str):
                    fecha_str = self.fecha.replace('-', '')
                elif hasattr(self.fecha, 'strftime'):
                    fecha_str = self.fecha.strftime('%Y%m%d')
                else:
                    fecha_str = '2026'
                self.codigo_evidencia = f"EVI-{fecha_str}-{self.pk:04d}"
                updates.append('codigo_evidencia')
            if updates:
                super().save(update_fields=updates)
            return
        return super().save(*args, **kwargs)

    def __str__(self):
        cod = f"[{self.codigo}] " if self.codigo else ""
        return f"{cod}{self.fecha} - {self.solicitud[:50]}"

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
    id_funcionario = models.ForeignKey(
        Funcionario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='id_funcionario',
        related_name='evidencias_subidas',
        verbose_name='Funcionario que Sube'
    )
    codigo = models.CharField(max_length=50, unique=True)
    archivo_ruta = models.CharField(max_length=255, blank=True, null=True, verbose_name='Ruta / Nombre Archivo')
    imagen = models.ImageField(
        upload_to='evidencias/',
        null=True,
        blank=True,
        verbose_name='Imagen de Evidencia'
    )
    imagen_verificada = models.BooleanField(default=False)
    verificador_valido = models.BooleanField(default=False)
    resultado = models.IntegerField(default=0)
    estado_validacion = models.CharField(
        max_length=20,
        choices=[
            ('Pendiente', 'Pendiente'),
            ('Aprobada', 'Aprobada'),
            ('Rechazada', 'Rechazada'),
            ('Corregir', 'Requiere Correción'),
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
    codigo = models.CharField(max_length=20, unique=True, blank=True, null=True, verbose_name='Código')
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

    def save(self, *args, **kwargs):
        if not self.codigo:
            kwargs.pop('force_insert', None)
            super().save(*args, **kwargs)
            self.codigo = f"TIP-{self.pk:02d}"
            return super().save(update_fields=['codigo'])
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"[{self.codigo}] {self.nombre}"


class SubAtencion(models.Model):
    id_subatencion = models.AutoField(primary_key=True)
    codigo = models.CharField(max_length=20, unique=True, blank=True, null=True, verbose_name='Código')
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

    def save(self, *args, **kwargs):
        if not self.codigo:
            kwargs.pop('force_insert', None)
            super().save(*args, **kwargs)
            self.codigo = f"SUB-{self.pk:02d}"
            return super().save(update_fields=['codigo'])
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"[{self.codigo}] {self.nombre} ({self.id_tipo.nombre})"


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
            kwargs.pop('force_insert', None)
            super().save(*args, **kwargs)
            self.folio = f"ATC-{self.pk:05d}"
            return super().save(update_fields=['folio'])
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.folio or f'ATC-{self.pk}'} - {self.solicitante}"


class GestionSocial(models.Model):
    id_gestion_social = models.AutoField(primary_key=True)
    codigo = models.CharField(max_length=30, unique=True, blank=True, null=True, verbose_name='Código Social')
    fecha_ingreso = models.DateField(verbose_name='Fecha de Ingreso')

    id_tipo = models.ForeignKey(
        TipoAtencion,
        on_delete=models.RESTRICT,
        db_column='id_tipo',
        related_name='gestiones_sociales',
        verbose_name='Tipo de Atención Social'
    )
    id_subatencion = models.ForeignKey(
        SubAtencion,
        on_delete=models.RESTRICT,
        db_column='id_subatencion',
        related_name='gestiones_sociales',
        verbose_name='Sub Atención Social'
    )

    usuario = models.CharField(max_length=200, verbose_name='Nombre del Usuario / Solicitante')
    rut = models.CharField(max_length=20, blank=True, null=True, verbose_name='RUT')
    telefono = models.CharField(max_length=30, blank=True, null=True, verbose_name='Teléfono')
    direccion = models.CharField(max_length=250, blank=True, null=True, verbose_name='Dirección / Sector')

    requiere_visita = models.BooleanField(default=False, verbose_name='¿Requiere Visita en Terreno?')
    fecha_programada_visita = models.DateField(blank=True, null=True, verbose_name='Fecha Programada Visita')
    ingreso_tubo = models.BooleanField(default=False, verbose_name='¿Ingreso al Tubo de Trabajo?')
    observaciones = models.TextField(verbose_name='Observaciones del Caso / Situación Social')

    # Flujo multi-etapa de gestiones del Gestor Social
    primera_gestion = models.CharField(
        max_length=200,
        default='ATENCIÓN SOCIAL A USUARIO PRESENCIAL',
        verbose_name='Primera Gestión'
    )
    segunda_gestion = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name='Segunda Gestión'
    )
    fecha_visita = models.DateField(blank=True, null=True, verbose_name='Fecha de Visita Realizada')
    fecha_entrega_informe = models.DateField(blank=True, null=True, verbose_name='Fecha Entrega Informe')

    tercera_gestion = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name='Tercera Gestión'
    )
    fecha_entrega_beneficio = models.DateField(blank=True, null=True, verbose_name='Fecha Entrega Beneficio')

    id_funcionario = models.ForeignKey(
        Funcionario,
        on_delete=models.RESTRICT,
        db_column='id_funcionario',
        related_name='gestiones_sociales',
        verbose_name='Gestor Social Responsable'
    )
    id_delegacion = models.ForeignKey(
        Delegacion,
        on_delete=models.RESTRICT,
        db_column='id_delegacion',
        related_name='gestiones_sociales',
        verbose_name='Delegación'
    )

    estado = models.CharField(
        max_length=30,
        choices=[
            ('Ingresada', 'Ingresada'),
            ('En Proceso', 'En Proceso'),
            ('Visita Pendiente', 'Visita Pendiente'),
            ('Informe Entregado', 'Informe Entregado'),
            ('Resuelta', 'Resuelta'),
            ('Cerrada', 'Cerrada'),
        ],
        default='Ingresada'
    )
    imagen_verificada = models.BooleanField(default=False, verbose_name='Imagen Verificada')
    verificador_valido = models.IntegerField(default=1, verbose_name='Verificador Válido')
    resultado = models.IntegerField(default=1, verbose_name='Resultado')
    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'gestiones_sociales'
        verbose_name = 'Gestión Social'
        verbose_name_plural = 'Gestiones Sociales'
        ordering = ['-fecha_ingreso', '-id_gestion_social']

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
    def funcionario(self):
        return self.id_funcionario

    def save(self, *args, **kwargs):
        if not self.codigo:
            kwargs.pop('force_insert', None)
            super().save(*args, **kwargs)
            self.codigo = f"SOC-{self.pk:05d}"
            return super().save(update_fields=['codigo'])
        return super().save(*args, **kwargs)

    def __str__(self):
        cod = f"[{self.codigo}] " if self.codigo else ""
        return f"{cod}{self.usuario} - {self.primera_gestion}"
