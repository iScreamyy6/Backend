from django.urls import path
from . import views

app_name = 'actividades'

urlpatterns = [
    path('', views.lista_actividades, name='lista_actividades'),
    path('actividad/<int:actividad_id>/', views.detalle_actividad, name='detalle_actividad'),
    path('evidencias/', views.lista_evidencias, name='lista_evidencias'),
    path('evidencia/<int:evidencia_id>/', views.detalle_evidencia, name='detalle_evidencia'),
]