import json
from django.conf import settings
from django.shortcuts import render
from django.http import Http404

def cargar_metas():
    ruta = settings.BASE_DIR / 'datos' / 'metas.json'
    with open(ruta, encoding='utf-8') as archivo:
        return json.load(archivo)

def cargar_personas():
    ruta = settings.BASE_DIR / 'datos' / 'personas.json'
    with open(ruta, encoding='utf-8') as archivo:
        return json.load(archivo)

def cargar_unidades():
    ruta = settings.BASE_DIR / 'datos' / 'organizacion.json'
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
    personas = cargar_personas()
    persona = next((p for p in personas if p['id'] == persona_id), None)
    if persona is None:
        # Fallback si el ID viene de metas.json
        persona = {
            'id': persona_id,
            'nombre': 'Funcionario Evaluado',
            'cargo': 'Gestor Territorial',
            'activo': True
        }

    # Definir ítems de evaluación típicos según el perfil del cargo
    metas_items = [
        {
            'item': 'ATENCIÓN DE USUARIO PRESENCIAL Y TELEFÓNICA',
            'descripcion': 'Atenciones registradas con nombre y teléfono de contacto',
            'ponderador': 25,
            'meta_periodo': 40,
            'avance_actual': 38,
            'pct_cumplimiento': 95.0,
            'pct_cumplimiento_barra': min(95.0, 100),
            'cumplimiento_ponderado': 23.75,
        },
        {
            'item': 'INFORMES SOCIALES Y FICHAS FIBE',
            'descripcion': 'Informes socioeconómicos entregados a DIDECO',
            'ponderador': 30,
            'meta_periodo': 20,
            'avance_actual': 18,
            'pct_cumplimiento': 90.0,
            'pct_cumplimiento_barra': min(90.0, 100),
            'cumplimiento_ponderado': 27.0,
        },
        {
            'item': 'GESTIÓN TERRITORIAL Y OPERATIVOS',
            'descripcion': 'Salidas a terreno, operativos de aseo y poda',
            'ponderador': 25,
            'meta_periodo': 15,
            'avance_actual': 14,
            'pct_cumplimiento': 93.3,
            'pct_cumplimiento_barra': min(93.3, 100),
            'cumplimiento_ponderado': 23.33,
        },
        {
            'item': 'EMERGENCIAS COMUNALES Y REUNIONES',
            'descripcion': 'Atención de siniestros, anegamientos y contingencias',
            'ponderador': 20,
            'meta_periodo': 10,
            'avance_actual': 9,
            'pct_cumplimiento': 90.0,
            'pct_cumplimiento_barra': min(90.0, 100),
            'cumplimiento_ponderado': 18.0,
        }
    ]

    total_felicitaciones = 1
    felicitaciones_bonus = 10  # +10% por carta formal
    total_reclamos = 0
    reclamos_penalizacion = 0

    base_ponderada = sum(m['cumplimiento_ponderado'] for m in metas_items)
    cumplimiento_total = round(min(base_ponderada + felicitaciones_bonus - reclamos_penalizacion, 150), 1)

    gestiones = [
        {
            'fecha': '06/07/2026',
            'solicitud': 'Solicitud de Reunión por vehículos mal estacionados',
            'accion': 'Gestionar Reunión con vecinos',
            'item_evaluacion': 'ATENCIÓN DE USUARIO PRESENCIAL Y TELEFÓNICA',
            'codigo_evidencia': 'EVI-2026-0901',
            'estado_evidencia': 'Aprobada'
        },
        {
            'fecha': '06/07/2026',
            'solicitud': 'Poda en Sector Uruguay con Pasaje Totoral',
            'accion': 'Gestionar Poda e inspección en terreno',
            'item_evaluacion': 'GESTIÓN TERRITORIAL Y OPERATIVOS',
            'codigo_evidencia': 'EVI-2026-0902',
            'estado_evidencia': 'Aprobada'
        },
        {
            'fecha': '01/07/2026',
            'solicitud': 'Documentación aporte económico por incendio',
            'accion': 'Visita Terreno y Entrega Informe',
            'item_evaluacion': 'INFORMES SOCIALES Y FICHAS FIBE',
            'codigo_evidencia': 'EVI-2026-0903',
            'estado_evidencia': 'Pendiente'
        }
    ]

    contexto = {
        'persona': persona,
        'metas_items': metas_items,
        'cumplimiento_total': cumplimiento_total,
        'total_actividades_validas': sum(m['avance_actual'] for m in metas_items),
        'total_felicitaciones': total_felicitaciones,
        'felicitaciones_bonus': felicitaciones_bonus,
        'total_reclamos': total_reclamos,
        'reclamos_penalizacion': reclamos_penalizacion,
        'gestiones': gestiones
    }
    return render(request, 'resultados/resultado_persona.html', contexto)

def tablero_unidad(request, unidad_id):
    unidades = cargar_unidades()
    delegacion = next((u for u in unidades if u['id'] == unidad_id), None)
    if delegacion is None:
        delegacion = {
            'id': unidad_id,
            'nombre': 'Delegación Municipal Las Compañías',
            'responsable': 'He-Man',
            'ambito': 'Las Compañías Alta y Baja'
        }

    metas = cargar_metas()
    equipo_desempeno = []
    for m in metas:
        equipo_desempeno.append({
            'id': m['id'],
            'area': m['area'],
            'responsable': m['responsable'],
            'avance': m['avance'],
            'avance_barra': min(m['avance'], 100),
            'estado_semaforo': m['estado_semaforo']
        })

    avances = [m['avance'] for m in metas]
    promedio_delegacion = round(sum(avances) / len(avances), 1) if avances else 0

    optimos = sum(1 for m in metas if m['estado_semaforo'] == 'verde')
    alertas = sum(1 for m in metas if m['estado_semaforo'] == 'amarillo')
    criticos = sum(1 for m in metas if m['estado_semaforo'] == 'rojo')

    contexto = {
        'delegacion': delegacion,
        'promedio_delegacion': promedio_delegacion,
        'funcionarios_optimo': optimos,
        'funcionarios_alerta': alertas,
        'funcionarios_critico': criticos,
        'equipo_desempeno': equipo_desempeno,
        'incidencias': {
            'licencias': 12,
            'vacaciones': 15,
            'emergencias': 8,
            'compensatorios': 4
        }
    }
    return render(request, 'resultados/tablero_unidad.html', contexto)

def informe_resumen(request):
    return render(request, 'resultados/informe_resumen.html', {})