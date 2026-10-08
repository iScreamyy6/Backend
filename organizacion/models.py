from django.db import models


class Delegacion(models.Model):
    id_delegacion = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=200, unique=True)
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

    def __str__(self):
        return self.nombre


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
