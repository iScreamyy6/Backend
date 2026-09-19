import json
from django.conf import settings
from django.shortcuts import render
from django.http import Http404

def cargar_unidades():
    ruta = settings.BASE_DIR / 'datos' / 'organizacion.json'
    with open(ruta, encoding='utf-8') as archivo:
        return json.load(archivo)

def cargar_personas():
    ruta = settings.BASE_DIR / 'datos' / 'personas.json'
    with open(ruta, encoding='utf-8') as archivo:
        return json.load(archivo)

def lista_unidades(request):
    unidades = cargar_unidades()
    contexto = {'unidades': unidades, 'cantidad': len(unidades)}
    return render(request, 'organizacion/lista_unidades.html', contexto)

def detalle_unidad(request, unidad_id):
    unidades = cargar_unidades()
    unidad = next((u for u in unidades if u['id'] == unidad_id), None)
    
    if unidad is None:
        raise Http404('La delegación solicitada no existe en el sistema.')
        
    return render(request, 'organizacion/detalle_unidad.html', {'unidad': unidad})

def lista_personas(request):
    personas = cargar_personas()
    contexto = {'personas': personas, 'cantidad': len(personas)}
    return render(request, 'organizacion/lista_personas.html', contexto)

def detalle_persona(request, persona_id):
    personas = cargar_personas()
    persona = next((p for p in personas if p['id'] == persona_id), None)
    
    if persona is None:
        raise Http404('El funcionario solicitado no existe en el sistema.')
        
    return render(request, 'organizacion/detalle_persona.html', {'persona': persona})