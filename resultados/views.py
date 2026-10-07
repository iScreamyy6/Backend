from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from organizacion.models import Delegacion, Funcionario
from actividades.models import Actividad
from .models import PeriodoEvaluacion, MetaFuncionario, IndicadorDelegacion


def lista_metas(request):
    q = request.GET.get('q', '').strip()
    metas = IndicadorDelegacion.objects.select_related('id_delegacion').all()
    if q:
        metas = metas.filter(
            Q(area__icontains=q) |
            Q(responsable__icontains=q) |
            Q(id_delegacion__nombre__icontains=q)
        )
    contexto = {
        'metas': metas,
        'cantidad': metas.count()
    }
    return render(request, 'resultados/lista_metas.html', contexto)



def detalle_meta(request, meta_id):
    meta = get_object_or_404(IndicadorDelegacion, pk=meta_id)
    return render(request, 'resultados/detalle_meta.html', {'meta': meta})


def resultado_persona(request, persona_id):
    persona = Funcionario.objects.filter(pk=persona_id).first()
    if persona is None:
        persona = Funcionario.objects.first()

    metas_qs = MetaFuncionario.objects.filter(id_funcionario=persona)
    if not metas_qs.exists():
        # Si no tiene metas específicas cargadas, buscar el primer funcionario con metas
        meta_ejemplo = MetaFuncionario.objects.first()
        if meta_ejemplo:
            persona = meta_ejemplo.id_funcionario
            metas_qs = MetaFuncionario.objects.filter(id_funcionario=persona)

    metas_items = []
    total_felicitaciones = 0
    total_reclamos = 0

    for m in metas_qs:
        pct = float(m.porcentaje_cumplimiento)
        ponderado = float(m.cumplimiento_ponderado)
        metas_items.append({
            'item': m.item,
            'descripcion': f'Meta: {m.meta_periodo} gestiones comprometidas',
            'ponderador': float(m.ponderador),
            'meta_periodo': m.meta_periodo,
            'avance_actual': m.avance_actual,
            'pct_cumplimiento': round(pct, 1),
            'pct_cumplimiento_barra': min(round(pct, 1), 100),
            'cumplimiento_ponderado': round(ponderado, 2),
        })
        total_felicitaciones += m.felicitaciones
        total_reclamos += m.reclamos

    if not metas_items:
        # Valores de demostración si la base no tiene metas para este id
        metas_items = [
            {
                'item': 'ATENCIÓN DE USUARIO PRESENCIAL Y TELEFÓNICA',
                'descripcion': 'Atenciones registradas con nombre y teléfono de contacto',
                'ponderador': 25,
                'meta_periodo': 40,
                'avance_actual': 38,
                'pct_cumplimiento': 95.0,
                'pct_cumplimiento_barra': 95.0,
                'cumplimiento_ponderado': 23.75,
            },
            {
                'item': 'INFORMES SOCIALES Y FICHAS FIBE',
                'descripcion': 'Informes socioeconómicos entregados a DIDECO',
                'ponderador': 30,
                'meta_periodo': 20,
                'avance_actual': 18,
                'pct_cumplimiento': 90.0,
                'pct_cumplimiento_barra': 90.0,
                'cumplimiento_ponderado': 27.0,
            },
        ]
        base_ponderada = sum(m['cumplimiento_ponderado'] for m in metas_items)
        cumplimiento_total = 95.0
        felicitaciones_bonus = 10
        total_felicitaciones = 1
        reclamos_penalizacion = 0
    else:
        felicitaciones_bonus = total_felicitaciones * 10
        reclamos_penalizacion = total_reclamos * 25
        base_ponderada = sum(m['cumplimiento_ponderado'] for m in metas_items)
        cumplimiento_total = round(min(max(base_ponderada + felicitaciones_bonus - reclamos_penalizacion, 0), 150), 1)

    # Gestiones reales desde la tabla Actividad
    gestiones_qs = Actividad.objects.filter(responsable__icontains=persona.nombre if persona else '')
    if not gestiones_qs.exists():
        gestiones_qs = Actividad.objects.all()[:4]

    gestiones = []
    for g in gestiones_qs:
        gestiones.append({
            'fecha': g.fecha.strftime('%d/%m/%Y'),
            'solicitud': g.solicitud,
            'accion': g.accion,
            'item_evaluacion': g.item_evaluacion,
            'codigo_evidencia': g.codigo_evidencia or 'EVI-SGR-00',
            'estado_evidencia': g.estado
        })

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
    delegacion = Delegacion.objects.filter(pk=unidad_id).first()
    if delegacion is None:
        delegacion = Delegacion.objects.first()

    indicadores = IndicadorDelegacion.objects.filter(id_delegacion=delegacion)
    if not indicadores.exists():
        indicadores = IndicadorDelegacion.objects.all()

    equipo_desempeno = []
    avances = []
    licencias_totales = 0
    vacaciones_totales = 0
    emergencias_totales = 0
    compensatorios_totales = 0

    for ind in indicadores:
        av = float(ind.avance_porcentaje)
        avances.append(av)
        equipo_desempeno.append({
            'id': ind.pk,
            'area': ind.area,
            'responsable': ind.responsable,
            'avance': av,
            'avance_barra': min(av, 100),
            'estado_semaforo': ind.estado_semaforo,
        })
        licencias_totales += ind.licencias
        vacaciones_totales += ind.vacaciones
        emergencias_totales += ind.emergencias
        compensatorios_totales += ind.compensatorios

    promedio_delegacion = round(sum(avances) / len(avances), 1) if avances else 0
    optimos = sum(1 for m in equipo_desempeno if m['estado_semaforo'] == 'verde')
    alertas = sum(1 for m in equipo_desempeno if m['estado_semaforo'] == 'amarillo')
    criticos = sum(1 for m in equipo_desempeno if m['estado_semaforo'] == 'rojo')

    contexto = {
        'delegacion': delegacion,
        'promedio_delegacion': promedio_delegacion,
        'funcionarios_optimo': optimos,
        'funcionarios_alerta': alertas,
        'funcionarios_critico': criticos,
        'equipo_desempeno': equipo_desempeno,
        'incidencias': {
            'licencias': licencias_totales or 12,
            'vacaciones': vacaciones_totales or 15,
            'emergencias': emergencias_totales or 8,
            'compensatorios': compensatorios_totales or 4
        }
    }
    return render(request, 'resultados/tablero_unidad.html', contexto)


def informe_resumen(request):
    return render(request, 'resultados/informe_resumen.html', {})