from django.db import models
from organizacion.models import Funcionario, Delegacion


class PeriodoEvaluacion(models.Model):
    nombre = models.CharField(max_length=100)  # ej: "1er Trimestre 2026"
    fecha_inicio = models.DateField()
    fecha_cierre = models.DateField()
    dias_totales = models.IntegerField(default=90)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Período de Evaluación'
        verbose_name_plural = 'Períodos de Evaluación'
        ordering = ['-fecha_inicio']

    def __str__(self):
        return f"{self.nombre} ({'Activo' if self.activo else 'Cerrado'})"


class MetaFuncionario(models.Model):
    funcionario = models.ForeignKey(
        Funcionario,
        on_delete=models.CASCADE,
        related_name='metas'
    )
    periodo = models.ForeignKey(
        PeriodoEvaluacion,
        on_delete=models.CASCADE,
        related_name='metas',
        null=True,
        blank=True
    )
    item = models.CharField(max_length=200, verbose_name='Ítem de Evaluación')
    ponderador = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text='Porcentaje de ponderación (ej: 25.00 para 25%)'
    )
    meta_periodo = models.IntegerField(verbose_name='Meta del Período')
    avance_actual = models.IntegerField(default=0, verbose_name='Avance Actual')
    felicitaciones = models.IntegerField(default=0)
    reclamos = models.IntegerField(default=0)

    class Meta:
        verbose_name = 'Meta de Funcionario'
        verbose_name_plural = 'Metas de Funcionarios'
        ordering = ['funcionario', 'item']

    @property
    def porcentaje_cumplimiento(self):
        if self.meta_periodo > 0:
            calculado = (self.avance_actual / self.meta_periodo) * 100
            ajuste = (self.felicitaciones * 10) - (self.reclamos * 25)
            total = calculado + ajuste
            return min(max(total, 0), 150)  # Tope 150% según regla de negocio
        return 0

    @property
    def cumplimiento_ponderado(self):
        return (float(self.ponderador) * float(self.porcentaje_cumplimiento)) / 100

    def __str__(self):
        return f"{self.funcionario.nombre} - {self.item}"


class IndicadorDelegacion(models.Model):
    delegacion = models.ForeignKey(
        Delegacion,
        on_delete=models.CASCADE,
        related_name='indicadores'
    )
    area = models.CharField(max_length=150)
    responsable = models.CharField(max_length=200)
    avance_porcentaje = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    estado_semaforo = models.CharField(
        max_length=10,
        choices=[
            ('verde', 'Verde (Óptimo)'),
            ('ambar', 'Ámbar (Alerta)'),
            ('rojo', 'Rojo (Crítico)'),
        ],
        default='verde'
    )
    licencias = models.IntegerField(default=0)
    vacaciones = models.IntegerField(default=0)
    emergencias = models.IntegerField(default=0)
    compensatorios = models.IntegerField(default=0)

    class Meta:
        verbose_name = 'Indicador de Delegación'
        verbose_name_plural = 'Indicadores de Delegaciones'

    def __str__(self):
        return f"{self.area} - {self.responsable} ({self.estado_semaforo})"

    @property
    def avance(self):
        return float(self.avance_porcentaje)

