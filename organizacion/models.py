from django.db import models


class Delegacion(models.Model):
    nombre = models.CharField(max_length=200, unique=True)
    ambito = models.CharField(max_length=150)
    responsable = models.CharField(max_length=200)
    foco_estrategico = models.TextField(blank=True)
    estado = models.CharField(
        max_length=20,
        choices=[('Activa', 'Activa'), ('Inactiva', 'Inactiva')],
        default='Activa'
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Delegación'
        verbose_name_plural = 'Delegaciones'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Funcionario(models.Model):
    nombre = models.CharField(max_length=200)
    cargo = models.CharField(max_length=150)
    delegacion = models.ForeignKey(
        Delegacion,
        on_delete=models.CASCADE,
        related_name='funcionarios'
    )
    activo = models.BooleanField(default=True)
    fecha_ingreso = models.DateField(null=True, blank=True)

    class Meta:
        verbose_name = 'Funcionario'
        verbose_name_plural = 'Funcionarios'
        ordering = ['nombre']

    def __str__(self):
        return f"{self.nombre} ({self.cargo})"
