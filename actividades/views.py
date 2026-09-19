import json
from django.conf import settings
from django.shortcuts import render
from django.http import Http404

def cargar_actividades():
    ruta = settings.BASE_DIR / 'datos' / 'actividades.json'
    with open(ruta, encoding='utf-8') as archivo:
        return json.load(archivo)

def lista_actividades(request):
    actividades = cargar_actividades()
    contexto = {'actividades': actividades, 'cantidad': len(actividades)}
    return render(request, 'actividades/lista_actividades.html', contexto)

def detalle_actividad(request, actividad_id):
    actividades = cargar_actividades()
    actividad = next((a for a in actividades if a['id'] == actividad_id), None)
    
    if actividad is None:
        raise Http404('El registro de actividad solicitado no existe.')
        
    return render(request, 'actividades/detalle_actividad.html', {'actividad': actividad})

def lista_evidencias(request):
    return render(request, 'actividades/lista_evidencias.html', {})

def detalle_evidencia(request, evidencia_id):
    raise Http404('Evidencia no encontrada.')