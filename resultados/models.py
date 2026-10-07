from django.db import models
from organizacion.models import Funcionario, Delegacion


class PeriodoEvaluacion(models.Model):
    id_periodo = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    fecha_inicio = models.DateField()
    fecha_cierre = models.DateField()
    dias_totales = models.IntegerField(default=90)
    dias_transcurridos = models.IntegerField(default=89)
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = 'periodos_evaluacion'
        verbose_name = 'Período de Evaluación'
        verbose_name_plural = 'Períodos de Evaluación'
        ordering = ['-fecha_inicio']

    def __str__(self):
        return f"{self.nombre} ({'Activo' if self.activo else 'Cerrado'})"


class MetaFuncionario(models.Model):
    id_meta = models.AutoField(primary_key=True)
    id_funcionario = models.ForeignKey(
        Funcionario,
        on_delete=models.CASCADE,
        db_column='id_funcionario',
        related_name='metas'
    )
    id_periodo = models.ForeignKey(
        PeriodoEvaluacion,
        on_delete=models.RESTRICT,
        db_column='id_periodo',
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
    porcentaje_cumplimiento = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    cumplimiento_ponderado = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    felicitaciones = models.IntegerField(default=0)
    reclamos = models.IntegerField(default=0)

    class Meta:
        db_table = 'metas_funcionario'
        verbose_name = 'Meta de Funcionario'
        verbose_name_plural = 'Metas de Funcionarios'
        ordering = ['id_funcionario', 'item']

    # Alias para templates
    @property
    def funcionario(self):
        return self.id_funcionario

    @property
    def periodo(self):
        return self.id_periodo

    def __str__(self):
        return f"{self.id_funcionario.nombre} - {self.item}"


class IndicadorDelegacion(models.Model):
    id_indicador = models.AutoField(primary_key=True)
    id_delegacion = models.ForeignKey(
        Delegacion,
        on_delete=models.CASCADE,
        db_column='id_delegacion',
        related_name='indicadores'
    )
    id_periodo = models.ForeignKey(
        PeriodoEvaluacion,
        on_delete=models.RESTRICT,
        db_column='id_periodo',
        related_name='indicadores',
        null=True,
        blank=True
    )
    area = models.CharField(max_length=150)
    responsable = models.CharField(max_length=200)
    avance_porcentaje = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    estado_semaforo = models.CharField(
        max_length=10,
        choices=[
            ('verde', 'Verde (Óptimo ≥ 98.9%)'),
            ('amarillo', 'Amarillo (Alerta ≥ 60%)'),
            ('rojo', 'Rojo (Crítico < 60%)'),
        ],
        default='verde'
    )
    licencias = models.IntegerField(default=0)
    vacaciones = models.IntegerField(default=0)
    emergencias = models.IntegerField(default=0)
    compensatorios = models.IntegerField(default=0)

    class Meta:
        db_table = 'indicadores_delegacion'
        verbose_name = 'Indicador de Delegación'
        verbose_name_plural = 'Indicadores de Delegaciones'

    def __str__(self):
        return f"{self.area} - {self.responsable} ({self.estado_semaforo})"

    # Alias para templates
    @property
    def delegacion(self):
        return self.id_delegacion

    @property
    def avance(self):
        return float(self.avance_porcentaje)
