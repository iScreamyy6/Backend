import json
from django.conf import settings
from django.shortcuts import render
from django.http import Http404

def cargar_metas():
    ruta = settings.BASE_DIR / 'datos' / 'metas.json'
    with open(ruta, encoding='utf-8') as archivo:
        return json.load(archivo)

def lista_metas(request):
    metas = cargar_metas()
    contexto = {'metas': metas, 'cantidad': len(metas)}
    return render(request, 'resultados/lista_metas.html', contexto)

def detalle_meta(request, meta_id):
    metas = cargar_metas()
    meta = next((m for m in metas if m['id'] == meta_id), None)
    
    if meta is None:
        raise Http404('El registro de meta solicitado no existe.')
        
    return render(request, 'resultados/detalle_meta.html', {'meta': meta})

def resultado_persona(request, persona_id):
    return render(request, 'resultados/resultado_persona.html', {})

def tablero_unidad(request, unidad_id):
    return render(request, 'resultados/tablero_unidad.html', {})

def informe_resumen(request):
    return render(request, 'resultados/informe_resumen.html', {})