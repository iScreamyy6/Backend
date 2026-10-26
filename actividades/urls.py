from django.urls import path
from . import views

app_name = 'actividades'

urlpatterns = [
    path('', views.lista_actividades, name='lista_actividades'),
    path('nueva/', views.formulario_actividad, name='formulario_actividad'),
    path('actividad/<int:actividad_id>/', views.detalle_actividad, name='detalle_actividad'),
    path('actividad/<int:actividad_id>/evidencia/', views.subir_evidencia_actividad, name='subir_evidencia_actividad'),
    path('social/', views.lista_gestiones_sociales, name='lista_gestiones_sociales'),
    path('social/nueva/', views.formulario_gestion_social, name='formulario_gestion_social'),
    path('social/<int:pk>/', views.detalle_gestion_social, name='detalle_gestion_social'),
    path('evidencias/', views.lista_evidencias, name='lista_evidencias'),
    path('evidencia/<int:evidencia_id>/', views.detalle_evidencia, name='detalle_evidencia'),
]