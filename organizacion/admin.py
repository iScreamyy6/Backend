from django.contrib import admin
from .models import Delegacion, Funcionario


class FuncionarioInline(admin.TabularInline):
    model = Funcionario
    extra = 1
    fields = ('nombre', 'cargo', 'activo', 'fecha_ingreso')


@admin.register(Delegacion)
class DelegacionAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'ambito', 'responsable', 'estado', 'fecha_creacion')
    list_filter = ('estado', 'ambito')
    search_fields = ('nombre', 'responsable', 'ambito')
    ordering = ('id',)
    inlines = [FuncionarioInline]


@admin.register(Funcionario)
class FuncionarioAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'cargo', 'delegacion', 'activo', 'fecha_ingreso')
    list_filter = ('activo', 'delegacion', 'cargo')
    search_fields = ('nombre', 'cargo', 'delegacion__nombre')
    ordering = ('id',)
