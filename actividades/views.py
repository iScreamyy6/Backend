from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
import os

from .models import Actividad, Evidencia, TipoAtencion, SubAtencion, AtencionCiudadana, GestionSocial
from organizacion.models import Funcionario, Delegacion
from resultados.models import ItemMeta
from agenda.models import Compromiso


class EmptyValues:
    def __getattr__(self, name):
        return ''
    def __getitem__(self, key):
        return ''
    def get(self, key, default=''):
        return default


def lista_actividades(request):
    q = request.GET.get('q', '').strip()
    filtro = request.GET.get('filtro', 'todas').strip().lower()

    queryset = Actividad.objects.select_related(
        'id_funcionario', 'id_delegacion', 'id_tipo', 'id_subatencion', 'id_compromiso'
    ).all()

    # ── Filtro por rol y delegación ─────────────────────────────────────────
    # ROL-ADM y ROL-COORD tienen alcance COMUNAL (ven todo).
    # ROL-DEL y ROL-OPE solo ven gestiones de su propia delegación activa.
    if request.user.is_authenticated:
        try:
            perfil = request.user.perfil
            rol_codigo = perfil.rol.codigo if perfil.rol else ''
            alcance = perfil.rol.alcance_autorizado if perfil.rol else 'COMUNAL'
        except Exception:
            rol_codigo = ''
            alcance = 'COMUNAL'

        if alcance == 'DELEGACION':
            delegacion_activa_id = request.session.get('delegacion_activa_id') or (
                perfil.delegacion_activa_id if perfil.delegacion_activa else None
            )
            if delegacion_activa_id:
                queryset = queryset.filter(id_delegacion_id=delegacion_activa_id)
    # ──────────────────────────────────────────────────────────────────────────

    # Conteos estadísticos para las pestañas del módulo unificado
    total_todas = queryset.count()
    total_atencion = queryset.filter(solicitante__isnull=False).exclude(solicitante='').count()
    total_territorial = queryset.filter(es_gestion_social=False).count()
    total_social = queryset.filter(es_gestion_social=True).count()
    total_tubo = queryset.filter(ingreso_tubo=True).count()

    if filtro == 'atencion':
        queryset = queryset.filter(solicitante__isnull=False).exclude(solicitante='')
    elif filtro == 'territorial':
        queryset = queryset.filter(es_gestion_social=False)
    elif filtro == 'social':
        queryset = queryset.filter(es_gestion_social=True)
    elif filtro == 'tubo':
        queryset = queryset.filter(ingreso_tubo=True)

    if q:
        queryset = queryset.filter(
            Q(codigo__icontains=q) |
            Q(solicitud__icontains=q) |
            Q(solicitante__icontains=q) |
            Q(rut_solicitante__icontains=q) |
            Q(responsable__icontains=q) |
            Q(accion__icontains=q) |
            Q(item_evaluacion__icontains=q)
        )

    contexto = {
        'actividades': queryset,
        'cantidad': queryset.count(),
        'q': q,
        'filtro': filtro,
        'total_todas': total_todas,
        'total_atencion': total_atencion,
        'total_territorial': total_territorial,
        'total_social': total_social,
        'total_tubo': total_tubo,
    }
    return render(request, 'actividades/lista_actividades.html', contexto)


def detalle_actividad(request, actividad_id):
    actividad = get_object_or_404(
        Actividad.objects.select_related(
            'id_funcionario', 'id_delegacion', 'id_tipo', 'id_subatencion', 'id_compromiso'
        ),
        pk=actividad_id
    )
    return render(request, 'actividades/detalle_actividad.html', {'actividad': actividad})


@login_required(login_url='login')
def formulario_actividad(request):
    delegacion_activa_id = request.session.get('delegacion_activa_id')
    delegacion_activa = (
        Delegacion.objects.filter(pk=delegacion_activa_id).first()
        if delegacion_activa_id
        else Delegacion.objects.filter(estado='Activa').first()
    )
    funcionarios = Funcionario.objects.filter(activo=True).order_by('nombre')
    items_metas = ItemMeta.objects.filter(estado='Activo').order_by('nombre')
    tipos = TipoAtencion.objects.filter(estado='Activo').order_by('nombre')

    es_social_get = request.GET.get('tipo') == 'social'
    tubo_get = request.GET.get('tubo') == '1'

    ultimo = Actividad.objects.order_by('-id_actividad').first()
    siguiente_id = (ultimo.id_actividad + 1) if ultimo else 1
    prefijo_sugerido = "SOC" if es_social_get else "GES"
    codigo_sugerido = f"{prefijo_sugerido}-{siguiente_id:05d}"
    hoy = timezone.now().date()
    codigo_evi_sugerido = f"EVI-{hoy.strftime('%Y%m%d')}-{siguiente_id:04d}"

    if request.method == 'POST':
        fecha = request.POST.get('fecha') or hoy
        solicitud = request.POST.get('solicitud', '').strip()
        accion = request.POST.get('accion', '').strip()
        responsable_nombre = request.POST.get('responsable', '').strip()
        item_evaluacion = request.POST.get('item_evaluacion', '').strip()
        estado = request.POST.get('estado', 'Pendiente')

        # Datos solicitante / vecino
        solicitante = request.POST.get('solicitante', '').strip() or request.POST.get('contacto', '').strip()
        rut_solicitante = request.POST.get('rut_solicitante', '').strip()
        telefono = request.POST.get('telefono', '').strip()
        correo = request.POST.get('correo', '').strip()
        direccion = request.POST.get('direccion', '').strip()

        # Clasificación temática
        id_tipo = request.POST.get('id_tipo')
        id_subatencion = request.POST.get('id_subatencion')
        tipo_obj = TipoAtencion.objects.filter(pk=id_tipo).first() if id_tipo else None
        sub_obj = SubAtencion.objects.filter(pk=id_subatencion).first() if id_subatencion else None

        # Derivación a Tubo de Trabajo
        ingreso_tubo = request.POST.get('ingreso_tubo') in ('SI', 'si', 'on', 'true', '1')
        fecha_compromiso = request.POST.get('fecha_compromiso') or None
        area_apoyo = request.POST.get('area_apoyo', '').strip()
        territorio = request.POST.get('territorio', '').strip()

        # Especialización Gestor Social
        es_gestion_social = request.POST.get('es_gestion_social') in ('SI', 'si', 'on', 'true', '1') or es_social_get
        requiere_visita = request.POST.get('requiere_visita') in ('SI', 'si', 'on', 'true', '1')
        fecha_programada_visita = request.POST.get('fecha_programada_visita') or None
        observaciones_sociales = request.POST.get('observaciones_sociales', '').strip()
        primera_gestion = request.POST.get('primera_gestion', '').strip()
        segunda_gestion = request.POST.get('segunda_gestion', '').strip()
        fecha_visita = request.POST.get('fecha_visita') or None
        fecha_entrega_informe = request.POST.get('fecha_entrega_informe') or None
        tercera_gestion = request.POST.get('tercera_gestion', '').strip()
        fecha_entrega_beneficio = request.POST.get('fecha_entrega_beneficio') or None

        if not solicitud or not accion or not responsable_nombre or not item_evaluacion:
            messages.error(request, 'Por favor complete todos los campos obligatorios marcados con (*).')
            return render(request, 'actividades/formulario_actividad.html', {
                'funcionarios': funcionarios,
                'items_metas': items_metas,
                'tipos': tipos,
                'delegacion_activa': delegacion_activa,
                'codigo_sugerido': codigo_sugerido,
                'codigo_evi_sugerido': codigo_evi_sugerido,
                'es_social_default': es_gestion_social,
                'tubo_default': ingreso_tubo,
                'valores': request.POST,
            })

        funcionario_obj = Funcionario.objects.filter(nombre__iexact=responsable_nombre).first()
        if not funcionario_obj:
            funcionario_obj = Funcionario.objects.filter(nombre__icontains=responsable_nombre).first()
        if not funcionario_obj:
            funcionario_obj = funcionarios.first()

        # Crear actividad/gestión unificada
        actividad = Actividad.objects.create(
            usuario_creador=request.user if request.user.is_authenticated else None,
            id_funcionario=funcionario_obj,
            id_delegacion=delegacion_activa or (funcionario_obj.id_delegacion if funcionario_obj else None),
            fecha=fecha,
            solicitante=solicitante,
            rut_solicitante=rut_solicitante,
            telefono=telefono,
            correo=correo,
            direccion=direccion,
            territorio=territorio,
            contacto=solicitante,
            id_tipo=tipo_obj,
            id_subatencion=sub_obj,
            solicitud=solicitud,
            accion=accion,
            responsable=responsable_nombre,
            item_evaluacion=item_evaluacion,
            estado=estado,
            es_gestion_social=es_gestion_social,
            requiere_visita=requiere_visita,
            fecha_programada_visita=fecha_programada_visita,
            observaciones_sociales=observaciones_sociales,
            primera_gestion=primera_gestion,
            segunda_gestion=segunda_gestion,
            fecha_visita=fecha_visita,
            fecha_entrega_informe=fecha_entrega_informe,
            tercera_gestion=tercera_gestion,
            fecha_entrega_beneficio=fecha_entrega_beneficio,
            ingreso_tubo=ingreso_tubo,
            fecha_limite_tubo=fecha_compromiso,
            area_apoyo_tubo=area_apoyo,
        )

        # Si se decidió mandar a Tubo de Trabajo, crear y enlazar el compromiso
        codigo_tubo_asignado = None
        if ingreso_tubo:
            compromiso = Compromiso.objects.create(
                usuario_creador=request.user if request.user.is_authenticated else None,
                id_delegacion=delegacion_activa or (funcionario_obj.id_delegacion if funcionario_obj else Delegacion.objects.first()),
                id_responsable=funcionario_obj,
                id_actividad=actividad,
                fecha_solicitud=fecha,
                actividad=f"[{actividad.codigo}] {solicitud}",
                tipo='EXT',
                solicitante=solicitante or 'Vecino / Sector',
                territorio=territorio or (delegacion_activa.nombre if delegacion_activa else ''),
                responsable=responsable_nombre,
                fecha_compromiso=fecha_compromiso,
                area_apoyo=area_apoyo,
                estado='INGRESADO',
                observaciones=f"Gestión {actividad.codigo}: {accion}. Contacto: {telefono or 'N/A'}"
            )
            actividad.id_compromiso = compromiso
            actividad.save(update_fields=['id_compromiso'])
            codigo_tubo_asignado = compromiso.codigo

        # Procesar imagen de evidencia adjunta al momento de crear (opcional)
        imagen_file = request.FILES.get('imagen_evidencia')
        if imagen_file:
            Evidencia.objects.create(
                id_actividad=actividad,
                id_funcionario=funcionario_obj,
                codigo=actividad.codigo_evidencia or f"EVI-{actividad.pk:05d}",
                imagen=imagen_file,
                archivo_ruta=imagen_file.name,
                observacion=request.POST.get('observacion_evidencia', '').strip(),
                estado_validacion='Pendiente',
            )

        msg = f'¡Gestión guardada exitosamente! Se ha asignado Código de Gestión: {actividad.codigo} y Evidencia: {actividad.codigo_evidencia}.'
        if codigo_tubo_asignado:
            msg += f' Además, fue derivada exitosamente al Tubo de Trabajo (Código: {codigo_tubo_asignado}) y ya se visualiza en el Tablero Kanban.'
        if imagen_file:
            msg += ' La imagen de evidencia fue adjuntada correctamente.'

        messages.success(request, msg)
        return redirect('actividades:lista_actividades')

    return render(request, 'actividades/formulario_actividad.html', {
        'funcionarios': funcionarios,
        'items_metas': items_metas,
        'tipos': tipos,
        'delegacion_activa': delegacion_activa,
        'codigo_sugerido': codigo_sugerido,
        'codigo_evi_sugerido': codigo_evi_sugerido,
        'es_social_default': es_social_get,
        'tubo_default': tubo_get,
        'hoy': hoy.strftime('%Y-%m-%d'),
        'valores': EmptyValues(),
        'puede_subir_evidencia': True,
    })


# ==============================================================================
# GESTOR SOCIAL (MÓDULO DETALLADO CON FLUJO MULTI-ETAPA)
# ==============================================================================
def lista_gestiones_sociales(request):
    q = request.GET.get('q', '').strip()
    gestiones = GestionSocial.objects.select_related(
        'id_tipo', 'id_subatencion', 'id_funcionario', 'id_delegacion'
    ).all()

    if q:
        gestiones = gestiones.filter(
            Q(codigo__icontains=q) |
            Q(usuario__icontains=q) |
            Q(rut__icontains=q) |
            Q(observaciones__icontains=q) |
            Q(id_tipo__nombre__icontains=q) |
            Q(id_subatencion__nombre__icontains=q) |
            Q(id_funcionario__nombre__icontains=q)
        )

    contexto = {
        'gestiones': gestiones,
        'total': gestiones.count(),
        'q': q,
    }
    return render(request, 'actividades/lista_social.html', contexto)


@login_required(login_url='login')
def formulario_gestion_social(request):
    delegacion_activa_id = request.session.get('delegacion_activa_id')
    delegacion_activa = (
        Delegacion.objects.filter(pk=delegacion_activa_id).first()
        if delegacion_activa_id
        else Delegacion.objects.filter(estado='Activa').first()
    )
    tipos = TipoAtencion.objects.filter(estado='Activo').order_by('nombre')
    gestores = Funcionario.objects.filter(cargo__icontains='Social', activo=True)
    if not gestores.exists():
        gestores = Funcionario.objects.filter(activo=True)

    ultimo = GestionSocial.objects.order_by('-id_gestion_social').first()
    siguiente_id = (ultimo.id_gestion_social + 1) if ultimo else 1
    codigo_sugerido = f"SOC-{siguiente_id:05d}"
    hoy = timezone.now().date()

    if request.method == 'POST':
        fecha_ingreso = request.POST.get('fecha_ingreso') or hoy
        id_tipo = request.POST.get('id_tipo')
        id_subatencion = request.POST.get('id_subatencion')
        usuario = request.POST.get('usuario', '').strip()
        rut = request.POST.get('rut', '').strip()
        telefono = request.POST.get('telefono', '').strip()
        direccion = request.POST.get('direccion', '').strip()
        requiere_visita = request.POST.get('requiere_visita') == 'SI'
        fecha_programada_visita = request.POST.get('fecha_programada_visita') or None
        ingreso_tubo = request.POST.get('ingreso_tubo') == 'SI'
        observaciones = request.POST.get('observaciones', '').strip()

        primera_gestion = request.POST.get('primera_gestion', 'ATENCIÓN SOCIAL A USUARIO PRESENCIAL').strip()
        segunda_gestion = request.POST.get('segunda_gestion', '').strip()
        fecha_visita = request.POST.get('fecha_visita') or None
        fecha_entrega_informe = request.POST.get('fecha_entrega_informe') or None
        tercera_gestion = request.POST.get('tercera_gestion', '').strip()
        fecha_entrega_beneficio = request.POST.get('fecha_entrega_beneficio') or None

        id_funcionario = request.POST.get('id_funcionario')
        estado = request.POST.get('estado', 'Ingresada')

        if not usuario or not id_tipo or not id_subatencion or not observaciones:
            messages.error(request, 'Por favor complete todos los campos obligatorios del caso social (*).')
            return render(request, 'actividades/formulario_social.html', {
                'tipos': tipos,
                'gestores': gestores,
                'delegacion_activa': delegacion_activa,
                'codigo_sugerido': codigo_sugerido,
                'valores': request.POST,
            })

        tipo_obj = get_object_or_404(TipoAtencion, pk=id_tipo)
        sub_obj = get_object_or_404(SubAtencion, pk=id_subatencion, id_tipo=tipo_obj)
        funcionario_obj = Funcionario.objects.filter(pk=id_funcionario).first() or gestores.first()

        gestion = GestionSocial.objects.create(
            fecha_ingreso=fecha_ingreso,
            id_tipo=tipo_obj,
            id_subatencion=sub_obj,
            usuario=usuario,
            rut=rut,
            telefono=telefono,
            direccion=direccion,
            requiere_visita=requiere_visita,
            fecha_programada_visita=fecha_programada_visita,
            ingreso_tubo=ingreso_tubo,
            observaciones=observaciones,
            primera_gestion=primera_gestion,
            segunda_gestion=segunda_gestion,
            fecha_visita=fecha_visita,
            fecha_entrega_informe=fecha_entrega_informe,
            tercera_gestion=tercera_gestion,
            fecha_entrega_beneficio=fecha_entrega_beneficio,
            id_funcionario=funcionario_obj,
            id_delegacion=delegacion_activa or funcionario_obj.id_delegacion,
            estado=estado,
        )

        # Sincronizar automáticamente en el Módulo Unificado de Gestiones (Actividad)
        actividad = Actividad.objects.create(
            id_funcionario=funcionario_obj,
            id_delegacion=delegacion_activa or funcionario_obj.id_delegacion,
            id_gestion_social=gestion,
            fecha=fecha_ingreso,
            solicitante=usuario,
            rut_solicitante=rut,
            telefono=telefono,
            direccion=direccion,
            territorio=direccion or (delegacion_activa.nombre if delegacion_activa else ''),
            contacto=usuario,
            id_tipo=tipo_obj,
            id_subatencion=sub_obj,
            solicitud=f"Caso Social: {observaciones}",
            accion=f"1ª: {primera_gestion} | 2ª: {segunda_gestion}",
            responsable=funcionario_obj.nombre,
            item_evaluacion='INFORMES SOCIALES',
            es_gestion_social=True,
            requiere_visita=requiere_visita,
            fecha_programada_visita=fecha_programada_visita,
            observaciones_sociales=observaciones,
            primera_gestion=primera_gestion,
            segunda_gestion=segunda_gestion,
            fecha_visita=fecha_visita,
            fecha_entrega_informe=fecha_entrega_informe,
            tercera_gestion=tercera_gestion,
            fecha_entrega_beneficio=fecha_entrega_beneficio,
            estado=estado,
            ingreso_tubo=ingreso_tubo,
        )

        if ingreso_tubo:
            compromiso = Compromiso.objects.create(
                id_delegacion=delegacion_activa or funcionario_obj.id_delegacion,
                id_responsable=funcionario_obj,
                id_actividad=actividad,
                fecha_solicitud=fecha_ingreso,
                actividad=f"[Caso Social {gestion.codigo}] {sub_obj.nombre} para {usuario}",
                tipo='EXT',
                solicitante=usuario,
                territorio=direccion or (delegacion_activa.nombre if delegacion_activa else ''),
                responsable=funcionario_obj.nombre,
                estado='INGRESADO',
                observaciones=f"Detalle: {observaciones[:150]}. Requiere visita: {'Sí' if requiere_visita else 'No'}"
            )
            actividad.id_compromiso = compromiso
            actividad.save(update_fields=['id_compromiso'])

        messages.success(
            request,
            f'¡Ficha de Gestión Social registrada exitosamente! Folio Social asignado: {gestion.codigo}.'
            + (' (Se derivó automáticamente al Tubo de Trabajo).' if ingreso_tubo else '')
        )
        return redirect('actividades:lista_gestiones_sociales')

    return render(request, 'actividades/formulario_social.html', {
        'tipos': tipos,
        'gestores': gestores,
        'delegacion_activa': delegacion_activa,
        'codigo_sugerido': codigo_sugerido,
        'hoy': hoy.strftime('%Y-%m-%d'),
        'valores': EmptyValues(),
    })


def detalle_gestion_social(request, pk):
    gestion = get_object_or_404(
        GestionSocial.objects.select_related('id_tipo', 'id_subatencion', 'id_funcionario', 'id_delegacion'),
        pk=pk
    )
    return render(request, 'actividades/detalle_social.html', {'gestion': gestion})


# ==============================================================================
# EVIDENCIAS
# ==============================================================================
def lista_evidencias(request):
    q = request.GET.get('q', '').strip()
    evidencias = Evidencia.objects.select_related('id_actividad').all()
    if q:
        evidencias = evidencias.filter(
            Q(codigo__icontains=q) |
            Q(id_actividad__solicitud__icontains=q) |
            Q(id_actividad__responsable__icontains=q) |
            Q(observacion__icontains=q)
        )

    aprobadas = evidencias.filter(estado_validacion='Aprobada').count()
    pendientes = evidencias.filter(estado_validacion='Pendiente').count()
    rechazadas = evidencias.filter(estado_validacion__in=['Corregir', 'Rechazada']).count()

    contexto = {
        'evidencias': evidencias,
        'total_evidencias': evidencias.count(),
        'aprobadas': aprobadas,
        'pendientes': pendientes,
        'rechazadas': rechazadas,
    }
    return render(request, 'actividades/lista_evidencias.html', contexto)


def detalle_evidencia(request, evidencia_id):
    evidencia = get_object_or_404(Evidencia.objects.select_related('id_actividad'), pk=evidencia_id)
    return render(request, 'actividades/detalle_evidencia.html', {'evidencia': evidencia})


@login_required(login_url='login')
def subir_evidencia_actividad(request, actividad_id):
    """Vista para subir o agregar evidencia fotográfica sobre una gestión ya existente."""
    actividad = get_object_or_404(
        Actividad.objects.select_related('id_funcionario', 'id_delegacion'),
        pk=actividad_id
    )

    # Control de acceso: ROL-OPE y ROL-DEL solo pueden subir evidencias de su propia delegación
    if request.user.is_authenticated:
        try:
            perfil = request.user.perfil
            alcance = perfil.rol.alcance_autorizado if perfil.rol else 'COMUNAL'
            if alcance == 'DELEGACION' and actividad.id_delegacion:
                delegacion_activa_id = request.session.get('delegacion_activa_id') or (
                    perfil.delegacion_activa_id if perfil.delegacion_activa else None
                )
                if delegacion_activa_id and actividad.id_delegacion_id != delegacion_activa_id:
                    messages.error(request, 'No tiene permiso para subir evidencias de otra delegación.')
                    return redirect('actividades:lista_actividades')
        except Exception:
            pass

    evidencias_existentes = actividad.evidencias.all().order_by('-fecha_carga')

    if request.method == 'POST':
        imagen_file = request.FILES.get('imagen_evidencia')
        observacion = request.POST.get('observacion_evidencia', '').strip()

        if not imagen_file:
            messages.error(request, 'Debe seleccionar una imagen para subir como evidencia.')
            return render(request, 'actividades/subir_evidencia.html', {
                'actividad': actividad,
                'evidencias': evidencias_existentes,
            })

        # Determinar código único para esta evidencia (puede haber múltiples por gestión)
        num_ev = evidencias_existentes.count() + 1
        codigo_ev = f"{actividad.codigo_evidencia or actividad.codigo}-EV{num_ev:02d}"
        # Asegurar unicidad
        if Evidencia.objects.filter(codigo=codigo_ev).exists():
            import uuid
            codigo_ev = f"{actividad.codigo}-{uuid.uuid4().hex[:6].upper()}"

        # Obtener funcionario vinculado (preferiblemente el del usuario actual)
        funcionario_obj = None
        try:
            perfil = request.user.perfil
            delegacion_activa_id = request.session.get('delegacion_activa_id') or (
                perfil.delegacion_activa_id if perfil.delegacion_activa else None
            )
            if delegacion_activa_id:
                funcionario_obj = Funcionario.objects.filter(
                    id_delegacion_id=delegacion_activa_id, activo=True
                ).first()
        except Exception:
            pass
        if not funcionario_obj:
            funcionario_obj = actividad.id_funcionario

        Evidencia.objects.create(
            id_actividad=actividad,
            id_funcionario=funcionario_obj,
            codigo=codigo_ev,
            imagen=imagen_file,
            archivo_ruta=imagen_file.name,
            observacion=observacion,
            estado_validacion='Pendiente',
        )

        messages.success(
            request,
            f'¡Evidencia cargada correctamente para la gestión {actividad.codigo}! '
            f'Código de evidencia asignado: {codigo_ev}. Estado: Pendiente de validación.'
        )
        return redirect('actividades:subir_evidencia_actividad', actividad_id=actividad_id)

    return render(request, 'actividades/subir_evidencia.html', {
        'actividad': actividad,
        'evidencias': evidencias_existentes,
    })