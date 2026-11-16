from django.urls import path
from . import views

app_name = 'resultados'

urlpatterns = [
    path('', views.lista_metas, name='lista_metas'),
    path('meta/<int:meta_id>/', views.detalle_meta, name='detalle_meta'),
    path('persona/<int:persona_id>/', views.resultado_persona, name='resultado_persona'),
    path('tablero/<int:unidad_id>/', views.tablero_unidad, name='tablero_unidad'),
    path('informe/', views.informe_resumen, name='informe_resumen'),

    # Asignación de Metas a Funcionarios (SGR - Trimestral)
    path('asignaciones/', views.asignaciones_lista, name='asignaciones_lista'),
    path('asignaciones/nueva/', views.asignacion_crear, name='asignacion_crear'),
    path('asignaciones/<int:pk>/editar/', views.asignacion_editar, name='asignacion_editar'),
    path('asignaciones/<int:pk>/desactivar/', views.asignacion_desactivar, name='asignacion_desactivar'),
    path('api/ponderacion/', views.api_resumen_ponderacion, name='api_resumen_ponderacion'),
]