import json
from django.conf import settings
from django.shortcuts import render
from django.http import Http404

def cargar_compromisos():
    ruta = settings.BASE_DIR / 'datos' / 'compromisos.json'
    with open(ruta, encoding='utf-8') as archivo:
        return json.load(archivo)

def lista_compromisos(request):
    compromisos = cargar_compromisos()
    contexto = {'compromisos': compromisos, 'cantidad': len(compromisos)}
    return render(request, 'agenda/lista_compromisos.html', contexto)

def detalle_compromiso(request, compromiso_id):
    compromisos = cargar_compromisos()
    compromiso = next((c for c in compromisos if c['id'] == compromiso_id), None)
    
    if compromiso is None:
        raise Http404('El compromiso solicitado no existe en el tubo de trabajo.')
        
    return render(request, 'agenda/detalle_compromiso.html', {'compromiso': compromiso})

def resumen_agenda(request):
    return render(request, 'agenda/resumen_agenda.html', {})