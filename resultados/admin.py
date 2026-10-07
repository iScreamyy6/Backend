from django.contrib import admin
from .models import PeriodoEvaluacion, MetaFuncionario, IndicadorDelegacion


@admin.register(PeriodoEvaluacion)
class PeriodoEvaluacionAdmin(admin.ModelAdmin):
    list_display = ('id_periodo', 'nombre', 'fecha_inicio', 'fecha_cierre', 'dias_totales', 'activo')
    list_filter = ('activo',)
    search_fields = ('nombre',)
    ordering = ('-fecha_inicio',)


@admin.register(MetaFuncionario)
class MetaFuncionarioAdmin(admin.ModelAdmin):
    list_display = (
        'id_meta',
        'id_funcionario',
        'id_periodo',
        'item',
        'ponderador',
        'meta_periodo',
        'avance_actual',
        'porcentaje_cumplimiento',
        'felicitaciones',
        'reclamos',
    )
    list_filter = ('id_periodo', 'id_funcionario__id_delegacion')
    search_fields = ('item', 'id_funcionario__nombre')
    ordering = ('id_funcionario', 'id_meta')


@admin.register(IndicadorDelegacion)
class IndicadorDelegacionAdmin(admin.ModelAdmin):
    list_display = (
        'id_indicador',
        'id_delegacion',
        'area',
        'responsable',
        'avance_porcentaje',
        'estado_semaforo',
        'licencias',
        'vacaciones',
        'emergencias',
    )
    list_filter = ('estado_semaforo', 'id_delegacion')
    search_fields = ('area', 'responsable', 'id_delegacion__nombre')
    ordering = ('id_delegacion', 'id_indicador')
