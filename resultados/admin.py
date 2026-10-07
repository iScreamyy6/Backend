from django.contrib import admin
from .models import PeriodoEvaluacion, MetaFuncionario, IndicadorDelegacion


@admin.register(PeriodoEvaluacion)
class PeriodoEvaluacionAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'fecha_inicio', 'fecha_cierre', 'dias_totales', 'activo')
    list_filter = ('activo',)
    search_fields = ('nombre',)
    ordering = ('-fecha_inicio',)


@admin.register(MetaFuncionario)
class MetaFuncionarioAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'funcionario',
        'periodo',
        'item',
        'ponderador',
        'meta_periodo',
        'avance_actual',
        'get_porcentaje_cumplimiento',
        'felicitaciones',
        'reclamos',
    )
    list_filter = ('periodo', 'funcionario__delegacion')
    search_fields = ('item', 'funcionario__nombre')
    ordering = ('funcionario', 'id')

    @admin.display(description='% Cumplimiento')
    def get_porcentaje_cumplimiento(self, obj):
        return f"{obj.porcentaje_cumplimiento:.1f}%"


@admin.register(IndicadorDelegacion)
class IndicadorDelegacionAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'delegacion',
        'area',
        'responsable',
        'avance_porcentaje',
        'estado_semaforo',
        'licencias',
        'vacaciones',
        'emergencias',
    )
    list_filter = ('estado_semaforo', 'delegacion')
    search_fields = ('area', 'responsable', 'delegacion__nombre')
    ordering = ('delegacion', 'id')
