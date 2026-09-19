from django.urls import path
from . import views

app_name = 'resultados'

urlpatterns = [
    path('', views.lista_metas, name='lista_metas'),
    path('meta/<int:meta_id>/', views.detalle_meta, name='detalle_meta'),
    path('persona/<int:persona_id>/', views.resultado_persona, name='resultado_persona'),
    path('tablero/<int:unidad_id>/', views.tablero_unidad, name='tablero_unidad'),
    path('informe/', views.informe_resumen, name='informe_resumen'),
]