from django.contrib import admin
from .models import Actividad, Evidencia, TipoAtencion, SubAtencion, AtencionCiudadana


class EvidenciaInline(admin.TabularInline):
    model = Evidencia
    extra = 1
    fk_name = 'id_actividad'
    fields = ('codigo', 'estado_validacion', 'imagen_verificada', 'verificador_valido', 'resultado')


@admin.register(Actividad)
class ActividadAdmin(admin.ModelAdmin):
    list_display = (
        'id_actividad',
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
    ordering = ('-fecha', '-id_actividad')
    inlines = [EvidenciaInline]


@admin.register(Evidencia)
class EvidenciaAdmin(admin.ModelAdmin):
    list_display = (
        'id_evidencia',
        'codigo',
        'id_actividad',
        'estado_validacion',
        'imagen_verificada',
        'verificador_valido',
        'resultado',
        'fecha_carga',
    )
    list_filter = ('estado_validacion', 'imagen_verificada', 'resultado', 'fecha_carga')
    search_fields = ('codigo', 'observacion', 'id_actividad__solicitud')
    ordering = ('-fecha_carga', '-id_evidencia')


class SubAtencionInline(admin.TabularInline):
    model = SubAtencion
    extra = 2
    fields = ('codigo', 'nombre', 'estado')


@admin.register(TipoAtencion)
class TipoAtencionAdmin(admin.ModelAdmin):
    list_display = ('id_tipo', 'codigo', 'nombre', 'estado', 'fecha_creacion')
    list_filter = ('estado',)
    search_fields = ('codigo', 'nombre', 'descripcion')
    ordering = ('codigo',)
    inlines = [SubAtencionInline]


@admin.register(SubAtencion)
class SubAtencionAdmin(admin.ModelAdmin):
    list_display = ('id_subatencion', 'codigo', 'nombre', 'id_tipo', 'estado', 'fecha_creacion')
    list_filter = ('estado', 'id_tipo')
    search_fields = ('codigo', 'nombre', 'id_tipo__nombre')
    ordering = ('codigo',)


@admin.register(AtencionCiudadana)
class AtencionCiudadanaAdmin(admin.ModelAdmin):
    list_display = (
        'folio',
        'solicitante',
        'id_tipo',
        'id_subatencion',
        'id_delegacion',
        'id_usuario_responsable',
        'estado',
        'fecha_registro',
    )
    list_filter = ('estado', 'id_delegacion', 'id_tipo', 'fecha_registro')
    search_fields = ('folio', 'solicitante', 'rut_solicitante', 'telefono', 'descripcion')
    ordering = ('-fecha_registro',)

