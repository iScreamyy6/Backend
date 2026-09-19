from django.urls import path
from . import views

app_name = 'organizacion'

urlpatterns = [
    path('', views.lista_unidades, name='lista_unidades'),
    path('unidad/<int:unidad_id>/', views.detalle_unidad, name='detalle_unidad'),
    
    path('personas/', views.lista_personas, name='lista_personas'),
    path('persona/<int:persona_id>/', views.detalle_persona, name='detalle_persona'),
]