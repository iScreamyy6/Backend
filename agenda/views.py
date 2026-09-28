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

def formulario_compromiso(request):
    return render(request, 'agenda/formulario_compromiso.html', {})

def resumen_agenda(request):
    compromisos = cargar_compromisos()
    total = len(compromisos)
    col_ingresados = [c for c in compromisos if c.get('estado') == 'INGRESADO']
    col_pendientes = [c for c in compromisos if c.get('estado') == 'PENDIENTE']
    col_proceso = [c for c in compromisos if c.get('estado') == 'EN PROCESO']
    col_realizados = [c for c in compromisos if c.get('estado') == 'REALIZADO']

    tasa_resolucion = round((len(col_realizados) / total * 100) if total > 0 else 0, 1)

    contexto = {
        'total': total,
        'col_ingresados': col_ingresados,
        'col_pendientes': col_pendientes,
        'col_proceso': col_proceso,
        'col_realizados': col_realizados,
        'total_realizados': len(col_realizados),
        'total_proceso': len(col_proceso),
        'total_pendientes': len(col_pendientes),
        'tasa_resolucion': tasa_resolucion
    }
    return render(request, 'agenda/resumen_agenda.html', contexto)