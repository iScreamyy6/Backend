from django.urls import path
from . import views

app_name = 'agenda'

urlpatterns = [
    path('', views.lista_compromisos, name='lista_compromisos'),
    path('compromiso/<int:compromiso_id>/', views.detalle_compromiso, name='detalle_compromiso'),
    path('resumen/', views.resumen_agenda, name='resumen_agenda'),
]