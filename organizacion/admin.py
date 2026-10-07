from django.contrib import admin
from .models import Delegacion, Funcionario


class FuncionarioInline(admin.TabularInline):
    model = Funcionario
    extra = 1
    fields = ('nombre', 'cargo', 'activo', 'fecha_ingreso')
    fk_name = 'id_delegacion'


@admin.register(Delegacion)
class DelegacionAdmin(admin.ModelAdmin):
    list_display = ('id_delegacion', 'nombre', 'ambito', 'responsable', 'estado', 'fecha_creacion')
    list_filter = ('estado', 'ambito')
    search_fields = ('nombre', 'responsable', 'ambito')
    ordering = ('id_delegacion',)
    inlines = [FuncionarioInline]


@admin.register(Funcionario)
class FuncionarioAdmin(admin.ModelAdmin):
    list_display = ('id_funcionario', 'nombre', 'cargo', 'id_delegacion', 'activo', 'fecha_ingreso')
    list_filter = ('activo', 'id_delegacion', 'cargo')
    search_fields = ('nombre', 'cargo', 'id_delegacion__nombre')
    ordering = ('id_funcionario',)
