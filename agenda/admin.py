from django.contrib import admin
from .models import Compromiso


@admin.register(Compromiso)
class CompromisoAdmin(admin.ModelAdmin):
    list_display = (
        'id_compromiso',
        'fecha_solicitud',
        'actividad',
        'tipo',
        'solicitante',
        'responsable',
        'fecha_compromiso',
        'estado',
    )
    list_filter = ('estado', 'tipo', 'fecha_solicitud')
    search_fields = (
        'actividad',
        'solicitante',
        'responsable',
        'territorio',
        'area_apoyo',
    )
    ordering = ('-fecha_solicitud', '-id_compromiso')
