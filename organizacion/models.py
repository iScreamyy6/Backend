from django.db import models
from django.contrib.auth.models import User


class Delegacion(models.Model):
    id_delegacion = models.AutoField(primary_key=True)
    codigo = models.CharField(max_length=20, blank=True, null=True, verbose_name='Código')
    nombre = models.CharField(max_length=200, unique=True)
    direccion = models.CharField(max_length=250, blank=True, default='', verbose_name='Dirección')
    comuna = models.CharField(max_length=100, default='La Serena', verbose_name='Comuna')
    ambito = models.CharField(max_length=150)
    responsable = models.CharField(max_length=200)
    foco_estrategico = models.TextField(blank=True, null=True)
    estado = models.CharField(
        max_length=20,
        choices=[('Activa', 'Activa'), ('Inactiva', 'Inactiva')],
        default='Activa'
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'delegaciones'
        verbose_name = 'Delegación'
        verbose_name_plural = 'Delegaciones'
        ordering = ['nombre']

    @property
    def id(self):
        return self.pk

    def save(self, *args, **kwargs):
        if not self.codigo:
            # Primer save para obtener el PK (evitamos pasar force_insert al segundo)
            kwargs.pop('force_insert', None)
            super().save(*args, **kwargs)
            self.codigo = f"D{self.pk:02d}"
            # Segundo save solo actualiza el campo codigo (UPDATE, nunca INSERT)
            return super().save(update_fields=['codigo'])
        return super().save(*args, **kwargs)

    def __str__(self):
        cod = f"[{self.codigo}] " if self.codigo else ""
        return f"{cod}{self.nombre}"


class Rol(models.Model):
    id_rol = models.AutoField(primary_key=True)
    codigo = models.CharField(max_length=20, unique=True, verbose_name='Código')
    nombre = models.CharField(max_length=100, unique=True, verbose_name='Nombre del Rol')
    descripcion = models.TextField(blank=True, verbose_name='Descripción')
    alcance_autorizado = models.CharField(
        max_length=30,
        choices=[
            ('COMUNAL', 'Comunal (Todas las delegaciones)'),
            ('DELEGACION', 'Por Delegación Asignada'),
        ],
        default='DELEGACION',
        verbose_name='Alcance Autorizado'
    )
    permisos = models.CharField(
        max_length=255,
        default='Listar, Consultar, Crear, Editar',
        verbose_name='Permisos y Alcance'
    )
    estado = models.CharField(
        max_length=20,
        choices=[('Activo', 'Activo'), ('Inactivo', 'Inactivo')],
        default='Activo'
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'roles'
        verbose_name = 'Rol'
        verbose_name_plural = 'Roles'
        ordering = ['nombre']

    @property
    def id(self):
        return self.pk

    def __str__(self):
        return f"{self.nombre} ({self.get_alcance_autorizado_display()})"


class PerfilUsuario(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    rol = models.ForeignKey(Rol, on_delete=models.RESTRICT, null=True, blank=True, related_name='usuarios')
    delegacion_activa = models.ForeignKey(
        Delegacion,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='usuarios_activa',
        verbose_name='Delegación Activa'
    )
    delegaciones_autorizadas = models.ManyToManyField(
        Delegacion,
        blank=True,
        related_name='usuarios_autorizados',
        verbose_name='Delegaciones Autorizadas'
    )
    telefono = models.CharField(max_length=30, blank=True, null=True, verbose_name='Teléfono')
    estado = models.CharField(
        max_length=20,
        choices=[('Activo', 'Activo'), ('Inactivo', 'Inactivo')],
        default='Activo'
    )
    # Control de recuperación de contraseña de 6 dígitos
    codigo_recuperacion = models.CharField(max_length=6, blank=True, null=True)
    codigo_expiracion = models.DateTimeField(null=True, blank=True)
    intentos_fallidos = models.IntegerField(default=0)
    codigo_usado = models.BooleanField(default=False)
    ultimo_reenvio = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'perfiles_usuarios'
        verbose_name = 'Perfil de Usuario'
        verbose_name_plural = 'Perfiles de Usuarios'
        ordering = ['user__username']

    @property
    def id(self):
        return self.pk

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} - {self.rol.nombre if self.rol else 'Sin Rol'}"

    def delegaciones_disponibles(self):
        if self.rol and self.rol.alcance_autorizado == 'COMUNAL':
            return Delegacion.objects.filter(estado='Activa')
        return self.delegaciones_autorizadas.filter(estado='Activa')


class Funcionario(models.Model):
    id_funcionario = models.AutoField(primary_key=True)
    id_delegacion = models.ForeignKey(
        Delegacion,
        on_delete=models.RESTRICT,
        db_column='id_delegacion',
        related_name='funcionarios'
    )
    nombre = models.CharField(max_length=200)
    cargo = models.CharField(max_length=150)
    activo = models.BooleanField(default=True)
    fecha_ingreso = models.DateField(null=True, blank=True)

    class Meta:
        db_table = 'funcionarios'
        verbose_name = 'Funcionario'
        verbose_name_plural = 'Funcionarios'
        ordering = ['nombre']

    def __str__(self):
        return f"{self.nombre} ({self.cargo})"

    @property
    def id(self):
        return self.pk

    # Alias para compatibilidad con templates que usen .delegacion
    @property
    def delegacion(self):
        return self.id_delegacion

