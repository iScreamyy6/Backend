import json
from django.conf import settings
from django.shortcuts import render
from django.http import Http404

def cargar_actividades():
    ruta = settings.BASE_DIR / 'datos' / 'actividades.json'
    with open(ruta, encoding='utf-8') as archivo:
        return json.load(archivo)

EVIDENCIAS_MOCK = [
    {
        'id': 1,
        'codigo': 'EVI-2026-0901',
        'actividad_id': 1,
        'actividad_solicitud': 'Solicitud de Reunión por vehículos mal estacionados',
        'actividad_resumen': 'Reunión con vecinos por vehículos mal estacionados en Pasaje Los Lirios',
        'responsable': 'Acuaman',
        'fecha': '06/07/2026',
        'fecha_carga': '06/07/2026 16:30',
        'accion': 'Gestionar Reunión',
        'item_evaluacion': 'ATENCION DE USUARIO TELEFONO Y PRESENCIAL',
        'archivo_nombre': 'acta_reunion_vehiculos.jpg',
        'imagen_verificada': True,
        'verificador_valido': True,
        'resultado': 1,
        'estado': 'Aprobada',
        'contacto': 'María González',
        'telefono': '+56 9 8765 4321',
        'observaciones': 'Acta firmada por 8 vecinos presentes con timbre de delegación.'
    },
    {
        'id': 2,
        'codigo': 'EVI-2026-0902',
        'actividad_id': 2,
        'actividad_solicitud': 'Solicitud de Poda en Sector de Uruguay con Pasaje Totoral',
        'actividad_resumen': 'Poda y despeje de cables en Pasaje Totoral',
        'responsable': 'Acuaman',
        'fecha': '06/07/2026',
        'fecha_carga': '07/07/2026 10:15',
        'accion': 'Gestionar Poda',
        'item_evaluacion': 'ATENCION DE USUARIO TELEFONO Y PRESENCIAL',
        'archivo_nombre': 'registro_fotografico_poda.jpg',
        'imagen_verificada': True,
        'verificador_valido': True,
        'resultado': 1,
        'estado': 'Aprobada',
        'contacto': 'Carlos Muñoz',
        'telefono': '+56 9 5544 3322',
        'observaciones': 'Foto del antes y después enviada a cuadrilla de parques y jardines.'
    },
    {
        'id': 3,
        'codigo': 'EVI-2026-0903',
        'actividad_id': 3,
        'actividad_solicitud': 'Entrega de documentación para aporte económico por incendio',
        'actividad_resumen': 'Informe Social y Ficha FIBE entregada para subsidio de emergencia',
        'responsable': 'Flash',
        'fecha': '01/07/2026',
        'fecha_carga': '02/07/2026 12:45',
        'accion': 'Visita Terreno y Entrega Informe',
        'item_evaluacion': 'INFORMES SOCIALES',
        'archivo_nombre': 'informe_social_fibe_082.pdf',
        'imagen_verificada': False,
        'verificador_valido': True,
        'resultado': 0,
        'estado': 'Pendiente',
        'contacto': 'Rosa Valenzuela',
        'telefono': '+56 9 9988 7766',
        'observaciones': 'Falta firma del asistente social jefe en la hoja 3.'
    },
    {
        'id': 4,
        'codigo': 'EVI-2026-0904',
        'actividad_id': 4,
        'actividad_solicitud': 'Coordinación Gestión territorial actividad navidad',
        'actividad_resumen': 'Coordinación con comités de navidad y logística comunal',
        'responsable': 'Pantera Negra',
        'fecha': '08/07/2026',
        'fecha_carga': '08/07/2026 18:00',
        'accion': 'Reunión',
        'item_evaluacion': 'EMERGENCIA',
        'archivo_nombre': 'asistencia_comites_navidad.jpg',
        'imagen_verificada': False,
        'verificador_valido': False,
        'resultado': 0,
        'estado': 'Corregir',
        'contacto': 'Pedro Soto',
        'telefono': '+56 9 3322 1100',
        'observaciones': 'Foto borrosa, no se aprecia la lista de asistentes ni fecha legible.'
    }
]

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

def formulario_actividad(request):
    return render(request, 'actividades/formulario_actividad.html', {})

def lista_evidencias(request):
    aprobadas = sum(1 for e in EVIDENCIAS_MOCK if e['estado'] == 'Aprobada')
    pendientes = sum(1 for e in EVIDENCIAS_MOCK if e['estado'] == 'Pendiente')
    rechazadas = sum(1 for e in EVIDENCIAS_MOCK if e['estado'] == 'Corregir')

    contexto = {
        'evidencias': EVIDENCIAS_MOCK,
        'total_evidencias': len(EVIDENCIAS_MOCK),
        'aprobadas': aprobadas,
        'pendientes': pendientes,
        'rechazadas': rechazadas,
    }
    return render(request, 'actividades/lista_evidencias.html', contexto)

def detalle_evidencia(request, evidencia_id):
    evidencia = next((e for e in EVIDENCIAS_MOCK if e['id'] == evidencia_id), None)
    if evidencia is None:
        raise Http404('Evidencia no encontrada.')
    return render(request, 'actividades/detalle_evidencia.html', {'evidencia': evidencia})