from django.contrib import admin
from .models import Actividad, Evidencia, TipoAtencion, SubAtencion, AtencionCiudadana, GestionSocial, Vecino


@admin.register(Vecino)
class VecinoAdmin(admin.ModelAdmin):
    list_display = ('id_vecino', 'rut', 'nombre', 'telefono', 'correo', 'direccion', 'territorio', 'fecha_registro')
    search_fields = ('rut', 'nombre', 'telefono', 'correo', 'direccion', 'territorio')
    ordering = ('nombre',)



class EvidenciaInline(admin.TabularInline):
    model = Evidencia
    extra = 1
    fk_name = 'id_actividad'
    fields = ('codigo', 'estado_validacion', 'imagen_verificada', 'verificador_valido', 'resultado')


class EsSubgestionFilter(admin.SimpleListFilter):
    title = 'Nivel Jerárquico'
    parameter_name = 'nivel_jerarquico'

    def lookups(self, request, model_admin):
        return (
            ('principal', 'Gestiones Principales (Sin Padre)'),
            ('subgestion', 'Subgestiones de Seguimiento'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'principal':
            return queryset.filter(id_gestion_padre__isnull=True)
        if self.value() == 'subgestion':
            return queryset.filter(id_gestion_padre__isnull=False)
        return queryset


class SubgestionInline(admin.TabularInline):
    model = Actividad
    extra = 0
    fk_name = 'id_gestion_padre'
    fields = ('codigo', 'fecha', 'solicitud', 'accion', 'responsable', 'estado')
    verbose_name = 'Subgestión de Seguimiento'
    verbose_name_plural = 'Subgestiones de Seguimiento'


@admin.register(Actividad)
class ActividadAdmin(admin.ModelAdmin):
    list_display = (
        'id_actividad',
        'codigo',
        'id_gestion_padre',
        'fecha',
        'solicitud',
        'solicitante',
        'territorio',
        'responsable',
        'item_evaluacion',
        'estado',
        'codigo_evidencia',
        'ingreso_tubo',
    )
    list_filter = ('estado', 'item_evaluacion', 'ingreso_tubo', 'es_gestion_social', 'fecha', EsSubgestionFilter)
    search_fields = ('codigo', 'solicitud', 'accion', 'solicitante', 'territorio', 'responsable', 'contacto', 'codigo_evidencia')
    ordering = ('-fecha', '-id_actividad')
    inlines = [EvidenciaInline, SubgestionInline]


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


@admin.register(GestionSocial)
class GestionSocialAdmin(admin.ModelAdmin):
    list_display = (
        'codigo',
        'fecha_ingreso',
        'usuario',
        'id_tipo',
        'id_subatencion',
        'id_funcionario',
        'id_delegacion',
        'requiere_visita',
        'primera_gestion',
        'estado',
    )
    list_filter = ('estado', 'requiere_visita', 'ingreso_tubo', 'id_delegacion', 'id_tipo', 'id_funcionario')
    search_fields = ('codigo', 'usuario', 'rut', 'telefono', 'observaciones')
    ordering = ('-fecha_ingreso', '-id_gestion_social')

