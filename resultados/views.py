from decimal import Decimal, InvalidOperation
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.db.models import Q, Sum
from organizacion.models import Delegacion, Funcionario
from actividades.models import Actividad
from Municipalidad.views_mantenedores import es_admin_o_coord, generar_excel_institucional
from .models import PeriodoEvaluacion, MetaFuncionario, IndicadorDelegacion, ItemMeta


@login_required(login_url='login')
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



@login_required(login_url='login')
def detalle_meta(request, meta_id):
    meta = get_object_or_404(IndicadorDelegacion, pk=meta_id)
    return render(request, 'resultados/detalle_meta.html', {'meta': meta})


@login_required(login_url='login')
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
            'id_meta': m.pk,
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


@login_required(login_url='login')
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


# ==============================================================================
# ASIGNACIÓN DE METAS A FUNCIONARIOS (TRIMESTRAL / PONDERACIÓN <= 100%)
# ==============================================================================
@login_required(login_url='login')
def asignaciones_lista(request):
    q = request.GET.get('q', '').strip()
    funcionario_id = request.GET.get('funcionario', '').strip()
    periodo_id = request.GET.get('periodo', '').strip()
    exportar = request.GET.get('exportar') == 'excel'

    periodos = PeriodoEvaluacion.objects.all().order_by('-activo', '-fecha_inicio')
    funcionarios = Funcionario.objects.filter(activo=True).select_related('id_delegacion').order_by('nombre')

    periodo_seleccionado = None
    if periodo_id:
        periodo_seleccionado = PeriodoEvaluacion.objects.filter(pk=periodo_id).first()
    elif not request.GET:
        periodo_seleccionado = periodos.filter(activo=True).first()
        if periodo_seleccionado:
            periodo_id = str(periodo_seleccionado.pk)

    queryset = MetaFuncionario.objects.select_related(
        'id_funcionario',
        'id_funcionario__id_delegacion',
        'id_periodo'
    ).all().order_by('id_funcionario__nombre', 'item')

    if q:
        queryset = queryset.filter(
            Q(item__icontains=q) |
            Q(id_funcionario__nombre__icontains=q) |
            Q(id_funcionario__cargo__icontains=q) |
            Q(id_funcionario__id_delegacion__nombre__icontains=q)
        )
    if funcionario_id:
        queryset = queryset.filter(id_funcionario_id=funcionario_id)
    if periodo_id:
        queryset = queryset.filter(id_periodo_id=periodo_id)

    ponderacion_acumulada = None
    ponderacion_disponible = None
    funcionario_seleccionado = None
    if funcionario_id:
        funcionario_seleccionado = Funcionario.objects.filter(pk=funcionario_id).first()
        if periodo_id:
            ponderacion_acumulada = MetaFuncionario.objects.filter(
                id_funcionario_id=funcionario_id,
                id_periodo_id=periodo_id
            ).aggregate(Sum('ponderador'))['ponderador__sum'] or Decimal('0.00')
            ponderacion_disponible = max(Decimal('0.00'), Decimal('100.00') - ponderacion_acumulada)

    if exportar:
        columnas = [
            'Funcionario',
            'Cargo',
            'Delegación',
            'Trimestre / Período',
            'Ítem de Evaluación',
            'Ponderación (%)',
            'Meta Cuantitativa',
            'Avance Actual',
            '% Cumplimiento',
            'Cumplimiento Ponderado (%)'
        ]
        filas = [
            [
                m.id_funcionario.nombre,
                m.id_funcionario.cargo,
                m.id_funcionario.delegacion.nombre if m.id_funcionario.delegacion else 'Sin delegación',
                m.id_periodo.nombre if m.id_periodo else 'Sin período',
                m.item,
                f"{m.ponderador}%",
                m.meta_periodo,
                m.avance_actual,
                f"{m.porcentaje_cumplimiento}%",
                f"{m.cumplimiento_ponderado}%"
            ]
            for m in queryset
        ]
        return generar_excel_institucional('AsignacionMetas', 'asignacion_metas_funcionarios', columnas, filas)

    paginador = Paginator(queryset, 15)
    page_obj = paginador.get_page(request.GET.get('page'))

    contexto = {
        'page_obj': page_obj,
        'q': q,
        'funcionario_id': funcionario_id,
        'periodo_id': periodo_id,
        'funcionarios': funcionarios,
        'periodos': periodos,
        'periodo_seleccionado': periodo_seleccionado,
        'funcionario_seleccionado': funcionario_seleccionado,
        'ponderacion_acumulada': ponderacion_acumulada,
        'ponderacion_disponible': ponderacion_disponible,
        'total_registros': queryset.count(),
        'es_admin_coord': es_admin_o_coord(request.user),
    }
    return render(request, 'resultados/asignaciones_lista.html', contexto)


@login_required(login_url='login')
def asignacion_crear(request):
    if not es_admin_o_coord(request.user):
        messages.error(request, 'Acceso restringido: Solo supervisores, delegados o administradores pueden asignar metas a funcionarios.')
        return redirect('resultados:asignaciones_lista')

    funcionarios = Funcionario.objects.filter(activo=True).select_related('id_delegacion').order_by('nombre')
    periodos = PeriodoEvaluacion.objects.all().order_by('-activo', '-fecha_inicio')
    items_catalogo = ItemMeta.objects.filter(estado='Activo').order_by('nombre')

    funcionario_id = request.GET.get('funcionario_id') or ''
    periodo_id = request.GET.get('periodo_id') or ''
    if not periodo_id:
        p_act = periodos.filter(activo=True).first()
        if p_act:
            periodo_id = str(p_act.pk)

    if request.method == 'POST':
        func_id = request.POST.get('funcionario')
        per_id = request.POST.get('periodo')
        item_catalogo = request.POST.get('item_catalogo', '').strip()
        item_personalizado = request.POST.get('item', '').strip()
        item_final = item_personalizado or item_catalogo
        meta_cuantitativa = request.POST.get('meta_cuantitativa', '').strip()
        ponderador_str = request.POST.get('ponderador', '').strip().replace(',', '.')

        datos_previos = {
            'funcionario_id': func_id,
            'periodo_id': per_id,
            'item': item_personalizado,
            'item_catalogo': item_catalogo,
            'meta_cuantitativa': meta_cuantitativa,
            'ponderador': ponderador_str
        }

        # 1. Validación de Funcionario
        if not func_id:
            messages.error(request, 'Debe seleccionar el funcionario al cual asignar la meta.')
            return render(request, 'resultados/asignacion_formulario.html', {
                'datos': datos_previos,
                'funcionarios': funcionarios,
                'periodos': periodos,
                'items_catalogo': items_catalogo,
                'es_edicion': False,
            })
        funcionario = get_object_or_404(Funcionario, pk=func_id)

        # 2. Validación de Trimestre correspondiente (pertenencia y activo)
        if not per_id:
            messages.error(request, 'Debe seleccionar el trimestre correspondiente para la meta.')
            return render(request, 'resultados/asignacion_formulario.html', {
                'datos': datos_previos,
                'funcionarios': funcionarios,
                'periodos': periodos,
                'items_catalogo': items_catalogo,
                'es_edicion': False,
            })
        periodo = get_object_or_404(PeriodoEvaluacion, pk=per_id)
        if not periodo.activo:
            messages.error(
                request,
                f'El trimestre "{periodo.nombre}" se encuentra cerrado. Las metas solo pueden asignarse a trimestres activos y vigentes.'
            )
            return render(request, 'resultados/asignacion_formulario.html', {
                'datos': datos_previos,
                'funcionarios': funcionarios,
                'periodos': periodos,
                'items_catalogo': items_catalogo,
                'es_edicion': False,
            })

        # 3. Validación de Meta Cuantitativa (obligatoria y > 0)
        if not meta_cuantitativa:
            messages.error(request, 'Debe registrar la meta cuantitativa (número de gestiones comprometidas).')
            return render(request, 'resultados/asignacion_formulario.html', {
                'datos': datos_previos,
                'funcionarios': funcionarios,
                'periodos': periodos,
                'items_catalogo': items_catalogo,
                'es_edicion': False,
            })
        try:
            meta_cuantitativa_num = int(meta_cuantitativa)
            if meta_cuantitativa_num <= 0:
                raise ValueError()
        except (ValueError, TypeError):
            messages.error(request, 'La meta cuantitativa debe ser un valor entero positivo mayor a 0 (ej: 40).')
            return render(request, 'resultados/asignacion_formulario.html', {
                'datos': datos_previos,
                'funcionarios': funcionarios,
                'periodos': periodos,
                'items_catalogo': items_catalogo,
                'es_edicion': False,
            })

        # 4. Validación de Ítem de Evaluación
        if not item_final:
            messages.error(request, 'Debe seleccionar un ítem del catálogo o ingresar un nombre de meta.')
            return render(request, 'resultados/asignacion_formulario.html', {
                'datos': datos_previos,
                'funcionarios': funcionarios,
                'periodos': periodos,
                'items_catalogo': items_catalogo,
                'es_edicion': False,
            })

        if MetaFuncionario.objects.filter(id_funcionario=funcionario, id_periodo=periodo, item__iexact=item_final).exists():
            messages.error(request, f'El funcionario {funcionario.nombre} ya tiene asignada la meta "{item_final}" en el {periodo.nombre}.')
            return render(request, 'resultados/asignacion_formulario.html', {
                'datos': datos_previos,
                'funcionarios': funcionarios,
                'periodos': periodos,
                'items_catalogo': items_catalogo,
                'es_edicion': False,
            })

        # 5. Validación de Ponderación y Sumatoria (no superar 100%)
        if not ponderador_str:
            messages.error(request, 'Debe ingresar el porcentaje de ponderación.')
            return render(request, 'resultados/asignacion_formulario.html', {
                'datos': datos_previos,
                'funcionarios': funcionarios,
                'periodos': periodos,
                'items_catalogo': items_catalogo,
                'es_edicion': False,
            })
        try:
            pond_num = Decimal(ponderador_str)
            if pond_num <= Decimal('0'):
                raise ValueError()
        except (InvalidOperation, ValueError):
            messages.error(request, 'La ponderación debe ser un porcentaje numérico mayor a 0% (ej: 25.00).')
            return render(request, 'resultados/asignacion_formulario.html', {
                'datos': datos_previos,
                'funcionarios': funcionarios,
                'periodos': periodos,
                'items_catalogo': items_catalogo,
                'es_edicion': False,
            })

        suma_actual = MetaFuncionario.objects.filter(
            id_funcionario=funcionario,
            id_periodo=periodo
        ).aggregate(Sum('ponderador'))['ponderador__sum'] or Decimal('0.00')

        if suma_actual + pond_num > Decimal('100.00'):
            disponible = max(Decimal('0.00'), Decimal('100.00') - suma_actual)
            messages.error(
                request,
                f'La sumatoria de las ponderaciones de las metas asignadas no puede superar el 100%. '
                f'{funcionario.nombre} ya acumula {suma_actual}% en el {periodo.nombre}. '
                f'Intentó asignar {pond_num}%, lo que totalizaría {suma_actual + pond_num}% '
                f'(Ponderación máxima disponible: {disponible}%).'
            )
            return render(request, 'resultados/asignacion_formulario.html', {
                'datos': datos_previos,
                'funcionarios': funcionarios,
                'periodos': periodos,
                'items_catalogo': items_catalogo,
                'es_edicion': False,
                'suma_actual': suma_actual,
                'disponible': disponible,
            })

        # 6. Crear MetaFuncionario
        meta = MetaFuncionario(
            id_funcionario=funcionario,
            id_periodo=periodo,
            item=item_final,
            meta_periodo=meta_cuantitativa_num,
            ponderador=pond_num,
            avance_actual=0
        )
        meta.save()
        messages.success(
            request,
            f'Meta "{item_final}" asignada exitosamente a {funcionario.nombre} para el {periodo.nombre} '
            f'(Ponderación: {pond_num}%, Meta Cuantitativa: {meta_cuantitativa_num} gestiones).'
        )
        return redirect('resultados:asignaciones_lista')

    return render(request, 'resultados/asignacion_formulario.html', {
        'datos': {'funcionario_id': funcionario_id, 'periodo_id': periodo_id},
        'funcionarios': funcionarios,
        'periodos': periodos,
        'items_catalogo': items_catalogo,
        'es_edicion': False,
    })


@login_required(login_url='login')
def asignacion_editar(request, pk):
    if not es_admin_o_coord(request.user):
        messages.error(request, 'Acceso restringido: Solo supervisores, delegados o administradores pueden editar metas.')
        return redirect('resultados:asignaciones_lista')

    meta = get_object_or_404(MetaFuncionario.objects.select_related('id_funcionario', 'id_periodo'), pk=pk)
    funcionarios = Funcionario.objects.filter(activo=True).select_related('id_delegacion').order_by('nombre')
    periodos = PeriodoEvaluacion.objects.all().order_by('-activo', '-fecha_inicio')
    items_catalogo = ItemMeta.objects.filter(estado='Activo').order_by('nombre')

    if request.method == 'POST':
        item_catalogo = request.POST.get('item_catalogo', '').strip()
        item_personalizado = request.POST.get('item', '').strip()
        item_final = item_personalizado or item_catalogo
        meta_cuantitativa = request.POST.get('meta_cuantitativa', '').strip()
        ponderador_str = request.POST.get('ponderador', '').strip().replace(',', '.')
        per_id = request.POST.get('periodo')

        periodo = get_object_or_404(PeriodoEvaluacion, pk=per_id) if per_id else meta.id_periodo
        if periodo and not periodo.activo and periodo != meta.id_periodo:
            messages.error(request, f'No se puede reasignar la meta al trimestre cerrado "{periodo.nombre}".')
            return redirect('resultados:asignacion_editar', pk=pk)

        # Validación Meta Cuantitativa
        try:
            meta_cuantitativa_num = int(meta_cuantitativa)
            if meta_cuantitativa_num <= 0:
                raise ValueError()
        except (ValueError, TypeError):
            messages.error(request, 'La meta cuantitativa debe ser un valor entero positivo mayor a 0.')
            return redirect('resultados:asignacion_editar', pk=pk)

        # Validación Ponderación
        try:
            pond_num = Decimal(ponderador_str)
            if pond_num <= Decimal('0'):
                raise ValueError()
        except (InvalidOperation, ValueError, TypeError):
            messages.error(request, 'La ponderación debe ser un porcentaje numérico mayor a 0%.')
            return redirect('resultados:asignacion_editar', pk=pk)

        # Sumatoria de las demás metas
        suma_otras = MetaFuncionario.objects.filter(
            id_funcionario=meta.id_funcionario,
            id_periodo=periodo
        ).exclude(pk=meta.pk).aggregate(Sum('ponderador'))['ponderador__sum'] or Decimal('0.00')

        if suma_otras + pond_num > Decimal('100.00'):
            disp = max(Decimal('0.00'), Decimal('100.00') - suma_otras)
            messages.error(
                request,
                f'La sumatoria de las ponderaciones de las metas asignadas no puede superar el 100%. '
                f'{meta.id_funcionario.nombre} ya acumula {suma_otras}% en otras metas para el {periodo.nombre}. '
                f'Ponderación máxima disponible para esta meta: {disp}%.'
            )
            return redirect('resultados:asignacion_editar', pk=pk)

        meta.item = item_final or meta.item
        meta.id_periodo = periodo
        meta.meta_periodo = meta_cuantitativa_num
        meta.ponderador = pond_num
        meta.save()

        messages.success(request, f'Meta "{meta.item}" actualizada exitosamente para {meta.id_funcionario.nombre}.')
        return redirect('resultados:asignaciones_lista')

    datos = {
        'funcionario_id': meta.id_funcionario.pk,
        'periodo_id': meta.id_periodo.pk if meta.id_periodo else '',
        'item': meta.item,
        'meta_cuantitativa': meta.meta_periodo,
        'ponderador': meta.ponderador,
    }
    return render(request, 'resultados/asignacion_formulario.html', {
        'datos': datos,
        'meta': meta,
        'funcionarios': funcionarios,
        'periodos': periodos,
        'items_catalogo': items_catalogo,
        'es_edicion': True,
    })


@login_required(login_url='login')
def asignacion_desactivar(request, pk):
    if not es_admin_o_coord(request.user):
        messages.error(request, 'Acceso restringido: Solo supervisores o administradores pueden desactivar metas.')
        return redirect('resultados:asignaciones_lista')

    meta = get_object_or_404(MetaFuncionario.objects.select_related('id_funcionario', 'id_periodo'), pk=pk)

    if request.method == 'POST':
        item_nom = meta.item
        func_nom = meta.id_funcionario.nombre
        meta.delete()
        messages.success(request, f'Meta "{item_nom}" de {func_nom} desactivada / eliminada exitosamente.')
        return redirect('resultados:asignaciones_lista')

    return render(request, 'resultados/asignacion_desactivar_confirmar.html', {'meta': meta})


@login_required(login_url='login')
def api_resumen_ponderacion(request):
    func_id = request.GET.get('funcionario_id')
    per_id = request.GET.get('periodo_id')
    meta_id = request.GET.get('meta_id')

    if not func_id or not per_id:
        return JsonResponse({'error': 'Parámetros incompletos'}, status=400)

    periodo = PeriodoEvaluacion.objects.filter(pk=per_id).first()
    qs = MetaFuncionario.objects.filter(id_funcionario_id=func_id, id_periodo_id=per_id)
    if meta_id:
        qs = qs.exclude(pk=meta_id)

    total_pond = float(qs.aggregate(Sum('ponderador'))['ponderador__sum'] or Decimal('0.00'))
    disponible = max(0.0, round(100.0 - total_pond, 2))
    metas_list = [{'id': m.pk, 'item': m.item, 'ponderador': float(m.ponderador), 'meta': m.meta_periodo} for m in qs]

    return JsonResponse({
        'total_ponderacion': total_pond,
        'disponible': disponible,
        'periodo_activo': periodo.activo if periodo else False,
        'periodo_nombre': periodo.nombre if periodo else '',
        'metas_existentes': metas_list
    })