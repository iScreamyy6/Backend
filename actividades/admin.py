from django.contrib import admin
from .models import Actividad, Evidencia


class EvidenciaInline(admin.TabularInline):
    model = Evidencia
    extra = 1
    fields = ('codigo', 'estado_validacion', 'imagen_verificada', 'verificador_valido', 'resultado')


@admin.register(Actividad)
class ActividadAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'fecha',
        'solicitud',
        'responsable',
        'item_evaluacion',
        'estado',
        'codigo_evidencia',
        'ingreso_tubo',
    )
    list_filter = ('estado', 'item_evaluacion', 'ingreso_tubo', 'fecha')
    search_fields = ('solicitud', 'accion', 'responsable', 'contacto', 'codigo_evidencia')
    ordering = ('-fecha', '-id')
    inlines = [EvidenciaInline]


@admin.register(Evidencia)
class EvidenciaAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'codigo',
        'actividad',
        'estado_validacion',
        'imagen_verificada',
        'verificador_valido',
        'resultado',
        'fecha_carga',
    )
    list_filter = ('estado_validacion', 'imagen_verificada', 'resultado', 'fecha_carga')
    search_fields = ('codigo', 'observacion', 'actividad__solicitud')
    ordering = ('-fecha_carga', '-id')
