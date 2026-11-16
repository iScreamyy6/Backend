from django.db import models
from django.contrib.auth.models import User
from organizacion.models import Funcionario, Delegacion


class ItemMeta(models.Model):
    id_item = models.AutoField(primary_key=True)
    codigo = models.CharField(max_length=20, unique=True, blank=True, null=True, verbose_name='Código')
    nombre = models.CharField(max_length=200, unique=True, verbose_name='Nombre del Ítem')
    descripcion = models.TextField(blank=True, verbose_name='Descripción')
    tipo_meta = models.CharField(
        max_length=50,
        choices=[
            ('Cuantitativa', 'Cuantitativa (Numérica / Volumen)'),
            ('Cualitativa', 'Cualitativa (Hito / Cumplimiento)'),
        ],
        default='Cuantitativa',
        verbose_name='Tipo de Meta'
    )
    estado = models.CharField(
        max_length=20,
        choices=[('Activo', 'Activo'), ('Inactivo', 'Inactivo')],
        default='Activo'
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'items_metas'
        verbose_name = 'Ítem y Meta'
        verbose_name_plural = 'Ítems y Metas'
        ordering = ['codigo']

    @property
    def id(self):
        return self.pk

    def save(self, *args, **kwargs):
        if not self.codigo:
            kwargs.pop('force_insert', None)
            super().save(*args, **kwargs)
            self.codigo = f"ITM-{self.pk:02d}"
            return super().save(update_fields=['codigo'])
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"[{self.codigo}] {self.nombre}"


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

    @property
    def id(self):
        return self.pk

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
    usuario_registro = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='id_usuario_registro',
        related_name='metas_registradas',
        verbose_name='Usuario que Registró'
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

    @property
    def id(self):
        return self.pk

    # Alias para templates
    @property
    def funcionario(self):
        return self.id_funcionario

    @property
    def periodo(self):
        return self.id_periodo

    @property
    def usuario_asociado(self):
        """Retorna el usuario que registró la meta o la cuenta vinculada al funcionario."""
        if self.usuario_registro:
            return self.usuario_registro
        if self.id_funcionario and self.id_funcionario.user:
            return self.id_funcionario.user
        return None

    @property
    def valor_gestion_ponderado(self):
        """Porcentaje que aporta cada gestión individual a la evaluación global ponderada."""
        if self.meta_periodo and self.meta_periodo > 0 and self.ponderador:
            return round(float(self.ponderador) / float(self.meta_periodo), 2)
        return 0.0

    @property
    def valor_gestion_meta(self):
        """Porcentaje que aporta cada gestión individual a la meta cuantitativa."""
        if self.meta_periodo and self.meta_periodo > 0:
            return round(100.0 / float(self.meta_periodo), 2)
        return 0.0

    @property
    def estado_semaforo(self):
        pct = float(self.porcentaje_cumplimiento or 0)
        if pct >= 80.0:
            return 'verde'
        elif pct >= 60.0:
            return 'amarillo'
        return 'rojo'

    def clean(self):
        from django.core.exceptions import ValidationError
        from decimal import Decimal
        from django.db.models import Sum

        if not self.id_periodo:
            raise ValidationError({'id_periodo': 'Debe seleccionar un trimestre de evaluación válido.'})

        if self.id_periodo and not self.id_periodo.activo and not self.pk:
            raise ValidationError({'id_periodo': f'El trimestre {self.id_periodo.nombre} está cerrado o inactivo. No admite nuevas asignaciones.'})

        if self.meta_periodo is None or self.meta_periodo <= 0:
            raise ValidationError({'meta_periodo': 'La meta cuantitativa es obligatoria y debe ser un número entero mayor a 0.'})

        if self.ponderador is None or Decimal(str(self.ponderador)) <= Decimal('0'):
            raise ValidationError({'ponderador': 'La ponderación debe ser un porcentaje mayor a 0%.'})

        if self.id_funcionario and self.id_periodo and self.ponderador:
            qs = MetaFuncionario.objects.filter(
                id_funcionario=self.id_funcionario,
                id_periodo=self.id_periodo
            )
            if self.pk:
                qs = qs.exclude(pk=self.pk)
            suma_otras = qs.aggregate(Sum('ponderador'))['ponderador__sum'] or Decimal('0.00')

            if suma_otras + Decimal(str(self.ponderador)) > Decimal('100.00'):
                disp = max(Decimal('0.00'), Decimal('100.00') - suma_otras)
                raise ValidationError({
                    'ponderador': f'La sumatoria de ponderaciones no puede superar el 100%. El funcionario ya tiene acumulado {suma_otras}% en el {self.id_periodo.nombre}. Ponderación máxima disponible: {disp}%.'
                })

    def save(self, *args, **kwargs):
        from decimal import Decimal
        if self.meta_periodo and self.meta_periodo > 0 and self.ponderador:
            pct = (Decimal(self.avance_actual) / Decimal(self.meta_periodo)) * Decimal('100')
            self.porcentaje_cumplimiento = round(pct, 2)
            pct_aplicable = min(pct, Decimal('150.00'))
            self.cumplimiento_ponderado = round((pct_aplicable * Decimal(str(self.ponderador))) / Decimal('100.00'), 2)
        super().save(*args, **kwargs)

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

    @property
    def id(self):
        return self.pk

    # Alias para templates
    @property
    def delegacion(self):
        return self.id_delegacion

    @property
    def avance(self):
        return float(self.avance_porcentaje)
