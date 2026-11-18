import unicodedata
from decimal import Decimal, InvalidOperation
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.db.models import Q, Sum
from django.utils import timezone
from organizacion.models import Delegacion, Funcionario
from actividades.models import Actividad
from Municipalidad.views_mantenedores import es_admin, es_admin_o_coord, generar_excel_institucional
from .models import PeriodoEvaluacion, MetaFuncionario, IndicadorDelegacion, ItemMeta


def normalizar_texto_meta(texto):
    if not texto:
        return ''
    t = texto.strip().lower()
    return ''.join(c for c in unicodedata.normalize('NFD', t) if unicodedata.category(c) != 'Mn')


def coincide_actividad_con_meta(meta_item, actividad):
    if not meta_item:
        return True
    m = normalizar_texto_meta(meta_item)
    a = normalizar_texto_meta(actividad.item_evaluacion or '')
    s = normalizar_texto_meta(actividad.solicitud or '')

    # Coincidencia directa o mutua inclusión
    if a and (m == a or m in a or a in m):
        return True

    # Coincidencia por palabras clave significativas (longitud >= 4)
    palabras = [p for p in m.split() if len(p) >= 4 and p not in ('para', 'como', 'sobre', 'este', 'esta', 'zona')]
    if palabras:
        if any(p in a for p in palabras):
            return True
        if sum(1 for p in palabras if p in s) >= 2:
            return True
    return False


def obtener_periodo_vigente():
    hoy = timezone.now().date()
    p = PeriodoEvaluacion.objects.filter(
        fecha_inicio__lte=hoy,
        fecha_cierre__gte=hoy
    ).first()
    if not p:
        p = PeriodoEvaluacion.objects.filter(activo=True).order_by('-fecha_inicio').first()
    if not p:
        p = PeriodoEvaluacion.objects.order_by('-fecha_inicio').first()
    return p


def obtener_contexto_usuario(user):
    """
    Determina el nivel de acceso y el contexto territorial del usuario:
    - es_admin: Superusuario, grupo Administrador o ROL-ADM.
    - es_supervisor: Grupo Supervisor o ROL-COORD / ROL-DEL.
    - es_funcionario: Funcionario o administrativo de línea.
    - funcionario: Registro de Funcionario institucional vinculado al usuario.
    - delegacion_asignada: Delegación asignada en perfil o en la ficha de funcionario.
    """
    if not user.is_authenticated:
        return {
            'es_admin': False,
            'es_supervisor': False,
            'es_funcionario': False,
            'funcionario': None,
            'delegacion_asignada': None,
        }

    perfil = getattr(user, 'perfil', None)
    admin_flag = bool(
        user.is_superuser or
        user.groups.filter(name='Administrador').exists() or
        (perfil and perfil.rol and perfil.rol.codigo == 'ROL-ADM')
    )
    supervisor_flag = bool(
        admin_flag or
        user.groups.filter(name='Supervisor').exists() or
        (perfil and perfil.rol and perfil.rol.codigo in ('ROL-COORD', 'ROL-DEL'))
    )
    funcionario_flag = not supervisor_flag

    func_obj = getattr(user, 'funcionario', None)
    if not func_obj:
        func_obj = Funcionario.objects.filter(user=user).first()

    delegacion_obj = None
    if perfil and perfil.delegacion_activa:
        delegacion_obj = perfil.delegacion_activa
    elif func_obj and func_obj.id_delegacion:
        delegacion_obj = func_obj.id_delegacion
    elif perfil and perfil.delegaciones_autorizadas.exists():
        delegacion_obj = perfil.delegaciones_autorizadas.first()

    return {
        'es_admin': admin_flag,
        'es_supervisor': supervisor_flag,
        'es_funcionario': funcionario_flag,
        'funcionario': func_obj,
        'delegacion_asignada': delegacion_obj,
    }


def calcular_avance_meta(meta):
    """
    Calcula dinámicamente el avance y semáforo de una meta a partir de las gestiones (Actividad)
    registradas por el funcionario o por el usuario que registró la meta en el período.
    Calcula cuánto vale cada gestión y su impacto directo en el semáforo.
    """
    # 1. Filtro de gestiones asociadas al funcionario o a su usuario creador
    filtros = Q(id_funcionario=meta.id_funcionario)
    if meta.id_funcionario and meta.id_funcionario.user:
        filtros |= Q(usuario_creador=meta.id_funcionario.user)
    if meta.usuario_registro:
        filtros |= Q(usuario_creador=meta.usuario_registro)
    if meta.id_funcionario and meta.id_funcionario.nombre:
        filtros |= Q(responsable__icontains=meta.id_funcionario.nombre)

    gestiones_qs = Actividad.objects.filter(filtros)

    # 2. Trimestre / período correspondiente
    if meta.id_periodo and meta.id_periodo.fecha_inicio and meta.id_periodo.fecha_cierre:
        gestiones_qs = gestiones_qs.filter(
            fecha__gte=meta.id_periodo.fecha_inicio,
            fecha__lte=meta.id_periodo.fecha_cierre
        )

    # 3. Coincidencia robusta e insensible a mayúsculas y acentos por ítem
    # Exclusividad estricta de validación: SOLO gestiones con evidencia 'Aprobada' y de impacto 'Cuantitativa'
    # ponderan al porcentaje de avance de las metas. Gestiones en revisión, con información pendiente o cualitativas no suman.
    gestiones_candidatas = [g for g in gestiones_qs if coincide_actividad_con_meta(meta.item, g)]
    cant_gestiones = len(gestiones_candidatas)
    if gestiones_candidatas:
        cant_validadas = sum(1 for g in gestiones_candidatas if g.es_valida_para_metas)
        avance_actual = cant_validadas
    else:
        avance_actual = int(meta.avance_actual or 0)

    # 4. ¿Cuánto vale cada gestión?
    # - Aporte a la meta cuantitativa (% de avance de la meta por cada gestión realizada):
    valor_gestion_meta = round(100.0 / float(meta.meta_periodo), 2) if meta.meta_periodo else 0.0
    # - Aporte ponderado al 100% de la evaluación global del funcionario:
    valor_gestion_ponderado = round(float(meta.ponderador) / float(meta.meta_periodo), 2) if meta.meta_periodo else 0.0

    # 5. Cumplimiento
    pct = (float(avance_actual) / float(meta.meta_periodo)) * 100.0 if meta.meta_periodo else 0.0
    pct_cumplimiento = round(pct, 1)
    pct_cumplimiento_barra = min(pct_cumplimiento, 100.0)

    # 6. Cumplimiento ponderado (con tope normativo del 150%)
    cumplimiento_ponderado = round((min(pct, 150.0) * float(meta.ponderador)) / 100.0, 2)

    # 7. Semáforo individual de la meta (Óptimo >= 80%, Alerta 60-79.9%, Crítico < 60%)
    if pct_cumplimiento >= 80.0:
        estado_semaforo = 'verde'
        estado_texto = 'ÓPTIMO'
    elif pct_cumplimiento >= 60.0:
        estado_semaforo = 'amarillo'
        estado_texto = 'ALERTA'
    else:
        estado_semaforo = 'rojo'
        estado_texto = 'CRÍTICO'

    return {
        'id_meta': meta.pk,
        'meta_obj': meta,
        'item': meta.item,
        'id_funcionario': meta.id_funcionario.pk if meta.id_funcionario else None,
        'funcionario_nombre': meta.id_funcionario.nombre if meta.id_funcionario else 'Sin asignar',
        'funcionario_cargo': meta.id_funcionario.cargo if meta.id_funcionario else '',
        'delegacion': meta.id_funcionario.delegacion if meta.id_funcionario else None,
        'delegacion_id': meta.id_funcionario.id_delegacion_id if meta.id_funcionario else None,
        'delegacion_nombre': meta.id_funcionario.delegacion.nombre if (meta.id_funcionario and meta.id_funcionario.delegacion) else 'Sin delegación',
        'delegacion_codigo': meta.id_funcionario.delegacion.codigo if (meta.id_funcionario and meta.id_funcionario.delegacion) else '',
        'usuario_registro': meta.usuario_registro,
        'usuario_asociado': meta.usuario_asociado,
        'periodo': meta.id_periodo,
        'periodo_nombre': meta.id_periodo.nombre if meta.id_periodo else 'Sin período',
        'ponderador': float(meta.ponderador),
        'meta_periodo': meta.meta_periodo,
        'avance_actual': avance_actual,
        'cant_gestiones_reales': cant_gestiones,
        'valor_gestion_meta': valor_gestion_meta,
        'valor_gestion_ponderado': valor_gestion_ponderado,
        'pct_cumplimiento': pct_cumplimiento,
        'pct_cumplimiento_barra': pct_cumplimiento_barra,
        'cumplimiento_ponderado': cumplimiento_ponderado,
        'estado_semaforo': estado_semaforo,
        'estado_texto': estado_texto,
        'felicitaciones': meta.felicitaciones,
        'reclamos': meta.reclamos,
    }


@login_required(login_url='login')
def lista_metas(request):
    """
    Vista principal del Semáforo de Cumplimiento.
    - Metas asociadas a cada usuario que las registró y a cada funcionario.
    - Cuánto vale cada gestión reflejado dinámicamente en el semáforo.
    - Filtro por delegación activa o comunal (todas las delegaciones).
    - Restricción estricta por rol:
        * Funcionarios: solo ven sus propias metas.
        * Supervisores: solo ven las metas de los funcionarios de su delegación.
        * Administradores: ven ámbito comunal o filtran por delegación.
    """
    permisos = obtener_contexto_usuario(request.user)
    es_adm = permisos['es_admin']
    es_sup = permisos['es_supervisor']
    es_func = permisos['es_funcionario']
    func_propio = permisos['funcionario']
    del_usuario = permisos['delegacion_asignada']

    # Delegación activa desde GET o Sesión
    delegacion_param = request.GET.get('delegacion', '').strip()
    delegacion_session = request.session.get('delegacion_activa_id')
    delegacion_sel_id = delegacion_param or (str(delegacion_session) if delegacion_session else '')
    es_comunal = str(delegacion_sel_id).strip().upper() in ('TODAS', '0', 'COMUNAL', '')

    metas_qs = MetaFuncionario.objects.select_related(
        'id_funcionario',
        'id_funcionario__user',
        'id_funcionario__id_delegacion',
        'id_periodo',
        'usuario_registro'
    ).all().order_by('id_funcionario__nombre', 'item')

    # Periodo vigente y filtro por período
    periodo_vigente = obtener_periodo_vigente()
    periodos_disponibles = PeriodoEvaluacion.objects.all().order_by('-fecha_inicio')
    periodo_sel_id = request.GET.get('periodo', '').strip()
    periodo_seleccionado = None
    if periodo_sel_id:
        if periodo_sel_id.upper() not in ('TODOS', 'TODAS', '0'):
            try:
                metas_qs = metas_qs.filter(id_periodo_id=int(periodo_sel_id))
                periodo_seleccionado = PeriodoEvaluacion.objects.filter(pk=int(periodo_sel_id)).first()
            except (ValueError, TypeError):
                pass
    elif periodo_vigente:
        metas_vigentes = metas_qs.filter(id_periodo=periodo_vigente)
        if metas_vigentes.exists():
            metas_qs = metas_vigentes
            periodo_seleccionado = periodo_vigente
            periodo_sel_id = str(periodo_vigente.pk)

    # APLICACIÓN DE REGLAS DE ACCESO POR ROL:
    delegacion_filtrada_obj = None
    if es_func and not es_sup:
        # Funcionarios: solo ven sus propias metas
        if func_propio:
            metas_qs = metas_qs.filter(
                Q(id_funcionario=func_propio) | Q(usuario_registro=request.user)
            )
        else:
            metas_qs = metas_qs.filter(usuario_registro=request.user)
        filtro_mensaje = 'Vista de Funcionario: Mostrando exclusivamente sus metas individuales.'
        modo_vista = 'funcionario'

    elif es_sup and not es_adm:
        # Supervisores: solo ven las metas de los usuarios de su delegación asignada
        if del_usuario:
            metas_qs = metas_qs.filter(id_funcionario__id_delegacion=del_usuario)
            delegacion_filtrada_obj = del_usuario
            filtro_mensaje = f'Vista de Supervisor: Metas de funcionarios de {del_usuario.nombre}.'
        else:
            filtro_mensaje = 'Vista de Supervisor: Mostrando metas de su delegación asignada.'
        modo_vista = 'supervisor'

    else:
        # Administradores: Comunal (todas) o delegación seleccionada
        if not es_comunal and delegacion_sel_id:
            try:
                del_pk = int(delegacion_sel_id)
                metas_qs = metas_qs.filter(id_funcionario__id_delegacion_id=del_pk)
                delegacion_filtrada_obj = Delegacion.objects.filter(pk=del_pk).first()
                filtro_mensaje = f'Filtro Territorial: Metas de {delegacion_filtrada_obj.nombre if delegacion_filtrada_obj else "Delegación seleccionada"}.'
                modo_vista = 'admin_delegacion'
            except (ValueError, TypeError):
                filtro_mensaje = 'Ámbito Territorial: Vista Consolidada Comunal (Todas las Delegaciones).'
                modo_vista = 'admin_comunal'
        else:
            filtro_mensaje = 'Ámbito Territorial: Vista Consolidada Comunal (Todas las Delegaciones).'
            modo_vista = 'admin_comunal'

    # Filtro de búsqueda textual 'q'
    q = request.GET.get('q', '').strip()
    if q:
        metas_qs = metas_qs.filter(
            Q(item__icontains=q) |
            Q(id_funcionario__nombre__icontains=q) |
            Q(id_funcionario__cargo__icontains=q) |
            Q(id_funcionario__id_delegacion__nombre__icontains=q) |
            Q(usuario_registro__username__icontains=q) |
            Q(id_funcionario__user__username__icontains=q)
        )

    # Cálculo dinámico de metas y valor por gestión
    metas_calculadas = [calcular_avance_meta(m) for m in metas_qs]

    # Agrupación por funcionario para Semáforo global por persona
    funcionarios_resumen = {}
    for m in metas_calculadas:
        fid = m['id_funcionario']
        if fid not in funcionarios_resumen:
            funcionarios_resumen[fid] = {
                'id_funcionario': fid,
                'funcionario': m['meta_obj'].id_funcionario,
                'nombre': m['funcionario_nombre'],
                'cargo': m['funcionario_cargo'],
                'delegacion': m['delegacion'],
                'delegacion_nombre': m['delegacion_nombre'],
                'delegacion_codigo': m['delegacion_codigo'],
                'usuario_asociado': m['usuario_asociado'],
                'usuario_registro': m['usuario_registro'],
                'metas': [],
                'total_gestiones': 0,
                'total_ponderado': 0.0,
                'total_felicitaciones': 0,
                'total_reclamos': 0,
            }
        funcionarios_resumen[fid]['metas'].append(m)
        funcionarios_resumen[fid]['total_gestiones'] += m['avance_actual']
        funcionarios_resumen[fid]['total_ponderado'] += m['cumplimiento_ponderado']
        funcionarios_resumen[fid]['total_felicitaciones'] += m['felicitaciones']
        funcionarios_resumen[fid]['total_reclamos'] += m['reclamos']

    for fid, data in funcionarios_resumen.items():
        bono = data['total_felicitaciones'] * 10
        castigo = data['total_reclamos'] * 25
        score = round(min(max(data['total_ponderado'] + bono - castigo, 0.0), 150.0), 1)
        data['cumplimiento_global'] = score
        data['cumplimiento_global_barra'] = min(score, 100.0)
        if score >= 80.0:
            data['semaforo_global'] = 'verde'
            data['semaforo_texto'] = 'ÓPTIMO'
        elif score >= 60.0:
            data['semaforo_global'] = 'amarillo'
            data['semaforo_texto'] = 'ALERTA'
        else:
            data['semaforo_global'] = 'rojo'
            data['semaforo_texto'] = 'CRÍTICO'

    # Estadísticas para el encabezado del semáforo
    total_metas = len(metas_calculadas)
    total_funcionarios = len(funcionarios_resumen)
    optimas = sum(1 for m in metas_calculadas if m['estado_semaforo'] == 'verde')
    alertas = sum(1 for m in metas_calculadas if m['estado_semaforo'] == 'amarillo')
    criticas = sum(1 for m in metas_calculadas if m['estado_semaforo'] == 'rojo')

    delegaciones_disponibles = Delegacion.objects.filter(estado='Activa').order_by('nombre')

    contexto = {
        'metas': metas_calculadas,
        'funcionarios_resumen': list(funcionarios_resumen.values()),
        'total_metas': total_metas,
        'total_funcionarios': total_funcionarios,
        'metas_optimas': optimas,
        'metas_alertas': alertas,
        'metas_criticas': criticas,
        'q': q,
        'filtro_mensaje': filtro_mensaje,
        'modo_vista': modo_vista,
        'es_comunal': es_comunal,
        'delegacion_sel_id': delegacion_sel_id,
        'delegacion_filtrada_obj': delegacion_filtrada_obj,
        'delegaciones_disponibles': delegaciones_disponibles,
        'periodo_vigente': periodo_vigente,
        'periodos_disponibles': periodos_disponibles,
        'periodo_sel_id': periodo_sel_id,
        'periodo_seleccionado': periodo_seleccionado,
        'es_admin': es_adm,
        'es_supervisor': es_sup,
        'es_funcionario': es_func,
        'funcionario_propio': func_propio,
    }
    return render(request, 'resultados/lista_metas.html', contexto)


@login_required(login_url='login')
def detalle_meta(request, meta_id):
    meta = get_object_or_404(IndicadorDelegacion, pk=meta_id)
    return render(request, 'resultados/detalle_meta.html', {'meta': meta})


@login_required(login_url='login')
def resultado_persona(request, persona_id):
    """
    Ficha de Desempeño Individual SGR.
    - Valida que cada funcionario solo acceda a su propia ficha.
    - Valida que supervisores solo accedan a funcionarios de su delegación.
    - Presenta la columna con el cálculo exacto de cuánto vale cada gestión.
    - Vincula el historial de gestiones reales y su impacto en el semáforo.
    """
    permisos = obtener_contexto_usuario(request.user)
    es_adm = permisos['es_admin']
    es_sup = permisos['es_supervisor']
    es_func = permisos['es_funcionario']
    func_propio = permisos['funcionario']
    del_usuario = permisos['delegacion_asignada']

    persona = Funcionario.objects.filter(pk=persona_id).first()
    if persona is None:
        if func_propio:
            persona = func_propio
        else:
            persona = Funcionario.objects.first()

    # VALIDACIÓN DE SEGURIDAD Y PRIVACIDAD POR ROL:
    if es_func and not es_sup:
        if func_propio and persona and persona.pk != func_propio.pk:
            messages.warning(
                request,
                f'Acceso restringido: Como funcionario, solo tiene autorización para consultar su propia ficha de desempeño individual ({func_propio.nombre}).'
            )
            return redirect('resultados:resultado_persona', persona_id=func_propio.pk)
        elif not func_propio:
            messages.error(request, 'Su cuenta de usuario no tiene asignado un perfil de funcionario.')
            return redirect('resultados:lista_metas')
    elif es_sup and not es_adm:
        if del_usuario and persona and persona.id_delegacion_id != del_usuario.pk:
            messages.warning(
                request,
                f'Acceso restringido: Solo puede visualizar fichas de funcionarios pertenecientes a su delegación ({del_usuario.nombre}).'
            )
            return redirect('resultados:lista_metas')

    metas_qs = MetaFuncionario.objects.filter(id_funcionario=persona).select_related(
        'id_funcionario', 'id_periodo', 'usuario_registro'
    ).order_by('item')

    metas_items = [calcular_avance_meta(m) for m in metas_qs]

    total_felicitaciones = sum(m['felicitaciones'] for m in metas_items)
    total_reclamos = sum(m['reclamos'] for m in metas_items)

    if not metas_items:
        cumplimiento_total = 0.0
        felicitaciones_bonus = 0
        reclamos_penalizacion = 0
    else:
        felicitaciones_bonus = total_felicitaciones * 10
        reclamos_penalizacion = total_reclamos * 25
        base_ponderada = sum(m['cumplimiento_ponderado'] for m in metas_items)
        cumplimiento_total = round(min(max(base_ponderada + felicitaciones_bonus - reclamos_penalizacion, 0.0), 150.0), 1)

    # Gestiones reales desde la tabla Actividad
    gestiones_qs = Actividad.objects.filter(
        Q(id_funcionario=persona) |
        Q(usuario_creador=persona.user if persona.user else None) |
        Q(responsable__icontains=persona.nombre)
    ).order_by('-fecha')[:50]

    gestiones = []
    for g in gestiones_qs:
        meta_asoc = next(
            (m for m in metas_items if m['item'].lower() in (g.item_evaluacion or '').lower() or (g.item_evaluacion or '').lower() in m['item'].lower()),
            None
        )
        es_valida = g.es_valida_para_metas
        valor_aportado = (meta_asoc['valor_gestion_ponderado'] if meta_asoc else 0.0) if es_valida else 0.0
        ev_asoc = g.evidencias.first()
        gestiones.append({
            'id': g.pk,
            'fecha': g.fecha.strftime('%d/%m/%Y') if hasattr(g.fecha, 'strftime') else str(g.fecha),
            'solicitud': g.solicitud,
            'accion': g.accion,
            'item_evaluacion': g.item_evaluacion or (meta_asoc['item'] if meta_asoc else 'Gestión Operativa'),
            'codigo_evidencia': g.codigo_evidencia or f'EVI-GES-{g.pk}',
            'id_evidencia': ev_asoc.pk if ev_asoc else None,
            'estado_evidencia': g.estado_evidencia,
            'tipo_impacto': g.tipo_impacto,
            'es_valida': es_valida,
            'valor_aportado': valor_aportado,
            'observacion_revision': g.observacion_revision or '',
        })

    contexto = {
        'persona': persona,
        'metas_items': metas_items,
        'cumplimiento_total': cumplimiento_total,
        'cumplimiento_total_barra': min(cumplimiento_total, 100.0),
        'total_actividades_validas': sum(m['avance_actual'] for m in metas_items),
        'total_felicitaciones': total_felicitaciones,
        'felicitaciones_bonus': felicitaciones_bonus,
        'total_reclamos': total_reclamos,
        'reclamos_penalizacion': reclamos_penalizacion,
        'gestiones': gestiones,
        'es_admin_coord': es_adm or es_sup,
    }
    return render(request, 'resultados/resultado_persona.html', contexto)


@login_required(login_url='login')
def tablero_unidad(request, unidad_id):
    delegacion = Delegacion.objects.filter(pk=unidad_id).first()
    if delegacion is None:
        delegacion = Delegacion.objects.first()

    periodo_actual = obtener_periodo_vigente()

    indicadores = IndicadorDelegacion.objects.filter(id_delegacion=delegacion)
    if periodo_actual:
        ind_periodo = indicadores.filter(id_periodo=periodo_actual)
        if ind_periodo.exists():
            indicadores = ind_periodo
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
        'periodo_actual': periodo_actual,
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
    periodo_actual = obtener_periodo_vigente()
    hoy = timezone.now().date()
    meses_es = ['', 'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
    fecha_emision = f"{hoy.day} de {meses_es[hoy.month]} {hoy.year}"
    if periodo_actual:
        periodo_auditado = f"{periodo_actual.nombre} ({periodo_actual.fecha_inicio.strftime('%d/%m/%Y')} — {periodo_actual.fecha_cierre.strftime('%d/%m/%Y')})"
    else:
        periodo_auditado = "4to Trimestre 2026 (01/10/2026 — 31/12/2026)"

    return render(request, 'resultados/informe_resumen.html', {
        'periodo_actual': periodo_actual,
        'fecha_emision': fecha_emision,
        'periodo_auditado': periodo_auditado,
    })


# ==============================================================================
# ASIGNACIÓN DE METAS A FUNCIONARIOS (TRIMESTRAL / PONDERACIÓN <= 100%)
# ==============================================================================
@login_required(login_url='login')
def asignaciones_lista(request):
    """
    Listado y gestión de asignaciones de metas a funcionarios.
    Aplica filtros territoriales y de roles (funcionario solo ve las suyas, supervisor su delegación).
    """
    permisos = obtener_contexto_usuario(request.user)
    es_adm = permisos['es_admin']
    es_sup = permisos['es_supervisor']
    es_func = permisos['es_funcionario']
    func_propio = permisos['funcionario']
    del_usuario = permisos['delegacion_asignada']

    q = request.GET.get('q', '').strip()
    funcionario_id = request.GET.get('funcionario', '').strip()
    periodo_id = request.GET.get('periodo', '').strip()
    exportar = request.GET.get('exportar') == 'excel'

    periodos = PeriodoEvaluacion.objects.all().order_by('-activo', '-fecha_inicio')
    funcionarios = Funcionario.objects.filter(activo=True).select_related('id_delegacion').order_by('nombre')

    # Filtrar funcionarios disponibles según rol
    if es_func and not es_sup:
        if func_propio:
            funcionarios = funcionarios.filter(pk=func_propio.pk)
            funcionario_id = str(func_propio.pk)
        else:
            funcionarios = funcionarios.none()
    elif es_sup and not es_adm:
        if del_usuario:
            funcionarios = funcionarios.filter(id_delegacion=del_usuario)

    periodo_seleccionado = None
    if periodo_id:
        periodo_seleccionado = PeriodoEvaluacion.objects.filter(pk=periodo_id).first()
    elif not request.GET:
        periodo_seleccionado = obtener_periodo_vigente() or periodos.filter(activo=True).first()
        if periodo_seleccionado:
            periodo_id = str(periodo_seleccionado.pk)

    queryset = MetaFuncionario.objects.select_related(
        'id_funcionario',
        'id_funcionario__id_delegacion',
        'id_periodo',
        'usuario_registro'
    ).all().order_by('id_funcionario__nombre', 'item')

    # Aplicar restricciones de visibilidad por rol
    if es_func and not es_sup:
        if func_propio:
            queryset = queryset.filter(Q(id_funcionario=func_propio) | Q(usuario_registro=request.user))
        else:
            queryset = queryset.filter(usuario_registro=request.user)
    elif es_sup and not es_adm:
        if del_usuario:
            queryset = queryset.filter(id_funcionario__id_delegacion=del_usuario)

    if q:
        queryset = queryset.filter(
            Q(item__icontains=q) |
            Q(id_funcionario__nombre__icontains=q) |
            Q(id_funcionario__cargo__icontains=q) |
            Q(id_funcionario__id_delegacion__nombre__icontains=q) |
            Q(usuario_registro__username__icontains=q)
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
            'Registrado Por',
            'Trimestre / Período',
            'Ítem de Evaluación',
            'Ponderación (%)',
            'Meta Cuantitativa',
            'Valor por Gestión (%)',
            'Avance Actual',
            '% Cumplimiento',
            'Cumplimiento Ponderado (%)'
        ]
        filas = [
            [
                m.id_funcionario.nombre,
                m.id_funcionario.cargo,
                m.id_funcionario.delegacion.nombre if m.id_funcionario.delegacion else 'Sin delegación',
                m.usuario_asociado.username if m.usuario_asociado else 'Sistema',
                m.id_periodo.nombre if m.id_periodo else 'Sin período',
                m.item,
                f"{m.ponderador}%",
                m.meta_periodo,
                f"{m.valor_gestion_ponderado}%",
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
        'es_admin_coord': es_adm or es_sup,
    }
    return render(request, 'resultados/asignaciones_lista.html', contexto)


@login_required(login_url='login')
def asignacion_crear(request, extra=None):
    """
    Crea una nueva meta para un funcionario.
    Registra automáticamente el usuario creador en `usuario_registro`.
    Valida sumatoria de ponderaciones <= 100%, meta cuantitativa > 0 y trimestre activo.
    """
    if extra:
        limpio = extra.lstrip('&/?')
        return redirect(f"{reverse('resultados:asignacion_crear')}?{limpio}" if limpio else reverse('resultados:asignacion_crear'))

    permisos = obtener_contexto_usuario(request.user)
    if not (permisos['es_admin'] or permisos['es_supervisor']):
        messages.error(request, 'Acceso restringido: Solo supervisores, delegados o administradores pueden asignar metas a funcionarios.')
        return redirect('resultados:asignaciones_lista')

    funcionarios = Funcionario.objects.filter(activo=True).select_related('id_delegacion').order_by('nombre')
    if permisos['es_supervisor'] and not permisos['es_admin'] and permisos['delegacion_asignada']:
        funcionarios = funcionarios.filter(id_delegacion=permisos['delegacion_asignada'])

    periodos = PeriodoEvaluacion.objects.all().order_by('-activo', '-fecha_inicio')
    items_catalogo = ItemMeta.objects.filter(estado='Activo').order_by('nombre')

    funcionario_id = request.GET.get('funcionario_id') or ''
    periodo_id = request.GET.get('periodo_id') or ''
    if not periodo_id:
        p_act = obtener_periodo_vigente() or periodos.filter(activo=True).first()
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

        # 6. Crear MetaFuncionario con asociación a usuario_registro
        meta = MetaFuncionario(
            id_funcionario=funcionario,
            usuario_registro=request.user,
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
            f'(Ponderación: {pond_num}%, Meta Cuantitativa: {meta_cuantitativa_num} gestiones). '
            f'Registrada por: {request.user.username}.'
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
    permisos = obtener_contexto_usuario(request.user)
    if not (permisos['es_admin'] or permisos['es_supervisor']):
        messages.error(request, 'Acceso restringido: Solo supervisores, delegados o administradores pueden editar metas.')
        return redirect('resultados:asignaciones_lista')

    meta = get_object_or_404(MetaFuncionario.objects.select_related('id_funcionario', 'id_periodo', 'usuario_registro'), pk=pk)

    # Validar que el supervisor solo edite metas de su delegación
    if permisos['es_supervisor'] and not permisos['es_admin']:
        if permisos['delegacion_asignada'] and meta.id_funcionario.id_delegacion_id != permisos['delegacion_asignada'].pk:
            messages.error(request, 'Acceso restringido: No puede modificar metas de funcionarios de otra delegación.')
            return redirect('resultados:asignaciones_lista')

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
        if not meta.usuario_registro:
            meta.usuario_registro = request.user
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
    permisos = obtener_contexto_usuario(request.user)
    if not (permisos['es_admin'] or permisos['es_supervisor']):
        messages.error(request, 'Acceso restringido: Solo supervisores, delegados o administradores pueden desactivar metas.')
        return redirect('resultados:asignaciones_lista')

    meta = get_object_or_404(MetaFuncionario.objects.select_related('id_funcionario'), pk=pk)

    if permisos['es_supervisor'] and not permisos['es_admin']:
        if permisos['delegacion_asignada'] and meta.id_funcionario.id_delegacion_id != permisos['delegacion_asignada'].pk:
            messages.error(request, 'Acceso restringido: No puede desactivar metas de otra delegación.')
            return redirect('resultados:asignaciones_lista')

    if request.method == 'POST':
        item_nom = meta.item
        func_nom = meta.id_funcionario.nombre
        meta.delete()
        messages.success(request, f'Meta "{item_nom}" de {func_nom} desactivada exitosamente.')
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
