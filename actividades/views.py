from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from django.http import JsonResponse
import os

from .models import Actividad, Evidencia, TipoAtencion, SubAtencion, AtencionCiudadana, GestionSocial, Vecino
from organizacion.models import Funcionario, Delegacion, CargoTipoGestion
from resultados.models import ItemMeta
from agenda.models import Compromiso


class EmptyValues:
    def __getattr__(self, name):
        return ''
    def __getitem__(self, key):
        return ''
    def get(self, key, default=''):
        return default


def es_admin_usuario(user):
    """Determina si el usuario autenticado tiene permisos de Administrador."""
    if not user or not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    perfil = getattr(user, 'perfil', None)
    return bool(perfil and perfil.rol and perfil.rol.codigo == 'ROL-ADM')


def obtener_tipos_por_cargo(usuario):
    """
    Retorna el QuerySet de TipoAtencion autorizados según el cargo del funcionario logueado.
    - Superusuarios y ROL-ADM tienen acceso a todos los tipos de gestión.
    - Usuarios no admin: se restringe a los tipos autorizados en CargoTipoGestion según su cargo.
    - Si el cargo es DISERCO: solo ve las opciones configuradas para DISERCO (ej. Territorial y Seguridad).
    """
    todos_los_tipos = TipoAtencion.objects.filter(estado='Activo').order_by('nombre')
    if not usuario or not usuario.is_authenticated:
        return todos_los_tipos

    if usuario.is_superuser:
        return todos_los_tipos

    perfil = getattr(usuario, 'perfil', None)
    if perfil and perfil.rol and perfil.rol.codigo in ('ROL-ADM', 'ROL-COORD'):
        return todos_los_tipos

    funcionario = getattr(usuario, 'funcionario', None)
    if not funcionario:
        funcionario = Funcionario.objects.filter(user=usuario).first()

    if not funcionario:
        return todos_los_tipos

    cargo = funcionario.cargo.strip()

    # 1. Búsqueda exacta en CargoTipoGestion
    mapeos = CargoTipoGestion.objects.filter(
        cargo__iexact=cargo,
        id_tipo__estado='Activo'
    ).values_list('id_tipo_id', flat=True)

    if mapeos.exists():
        return TipoAtencion.objects.filter(id_tipo__in=mapeos, estado='Activo').order_by('nombre')

    # 2. Búsqueda por subcadena de cargo
    cargo_upper = cargo.upper()
    if 'DISERCO' in cargo_upper:
        tipo_ids = CargoTipoGestion.objects.filter(cargo__icontains='DISERCO', id_tipo__estado='Activo').values_list('id_tipo_id', flat=True)
        if tipo_ids.exists():
            return TipoAtencion.objects.filter(id_tipo__in=tipo_ids, estado='Activo').order_by('nombre')
    elif 'SOCIAL' in cargo_upper:
        tipo_ids = CargoTipoGestion.objects.filter(cargo__icontains='Gestor Social', id_tipo__estado='Activo').values_list('id_tipo_id', flat=True)
        if tipo_ids.exists():
            return TipoAtencion.objects.filter(id_tipo__in=tipo_ids, estado='Activo').order_by('nombre')
    elif 'TERRITORIAL' in cargo_upper:
        tipo_ids = CargoTipoGestion.objects.filter(cargo__icontains='Territorial', id_tipo__estado='Activo').values_list('id_tipo_id', flat=True)
        if tipo_ids.exists():
            return TipoAtencion.objects.filter(id_tipo__in=tipo_ids, estado='Activo').order_by('nombre')

    return todos_los_tipos


def api_buscar_vecino(request):
    """
    Endpoint AJAX para buscar los datos de un solicitante/vecino por su RUT.
    Si se encuentra en la tabla Vecino (o historial), retorna los datos para autocompletar.
    Si no, indica que deben ingresarse manualmente.
    """
    rut = request.GET.get('rut', '').strip()
    if not rut:
        return JsonResponse({'encontrado': False, 'mensaje': 'Debe ingresar un RUT para buscar.'})

    rut_limpio = rut.replace('.', '').replace(' ', '').upper()

    # Buscar en tabla Vecino
    vecino = Vecino.objects.filter(
        Q(rut__iexact=rut) | Q(rut__iexact=rut_limpio)
    ).first()

    if not vecino:
        for v in Vecino.objects.all():
            if v.rut.replace('.', '').replace(' ', '').upper() == rut_limpio:
                vecino = v
                break

    # Fallback: buscar en actividades históricas
    if not vecino:
        act_hist = Actividad.objects.filter(
            Q(rut_solicitante__iexact=rut) | Q(rut_solicitante__iexact=rut_limpio)
        ).exclude(solicitante__isnull=True).exclude(solicitante='').first()
        if act_hist:
            vecino = Vecino.objects.create(
                rut=act_hist.rut_solicitante or rut,
                nombre=act_hist.solicitante or act_hist.contacto or '',
                telefono=act_hist.telefono or '',
                correo=act_hist.correo or '',
                direccion=act_hist.direccion or '',
                territorio=act_hist.territorio or '',
            )

    if vecino:
        return JsonResponse({
            'encontrado': True,
            'id_vecino': vecino.pk,
            'rut': vecino.rut,
            'nombre': vecino.nombre,
            'telefono': vecino.telefono or '',
            'correo': vecino.correo or '',
            'direccion': vecino.direccion or '',
            'territorio': vecino.territorio or '',
        })
    else:
        return JsonResponse({
            'encontrado': False,
            'mensaje': 'Vecino no encontrado en el registro comunal. Ingrese los datos manualmente para guardarlo.'
        })


def lista_actividades(request):
    q = request.GET.get('q', '').strip()
    filtro = request.GET.get('filtro', 'todas').strip()

    queryset = Actividad.objects.select_related(
        'id_funcionario', 'id_delegacion', 'id_tipo', 'id_subatencion', 'id_compromiso', 'id_vecino'
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

    # Tipos de gestión autorizados para el usuario
    tipos_autorizados = obtener_tipos_por_cargo(request.user)
    tipos_activos = TipoAtencion.objects.filter(estado='Activo').order_by('nombre')

    # Conteos estadísticos exclusivos por cada TipoAtencion
    conteo_por_tipo = {}
    for t in tipos_activos:
        conteo_por_tipo[t.codigo] = queryset.filter(id_tipo=t).count()

    total_todas = queryset.count()
    total_tubo = queryset.filter(ingreso_tubo=True).count()

    # Exclusividad estricta de tipo de gestión:
    # Una gestión pertenece a un único tipo de gestión y no se muestra en los demás.
    if filtro == 'tubo':
        queryset = queryset.filter(ingreso_tubo=True)
    elif filtro != 'todas':
        # Filtrar exactamente por el tipo seleccionado (por código o por ID)
        queryset = queryset.filter(Q(id_tipo__codigo__iexact=filtro) | Q(id_tipo_id__exact=filtro if filtro.isdigit() else 0))

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
        'total_tubo': total_tubo,
        'tipos_activos': tipos_activos,
        'conteo_por_tipo': conteo_por_tipo,
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

    es_admin = es_admin_usuario(request.user)
    
    # Obtener el funcionario del usuario autenticado (para auto-asignación si no es admin)
    funcionario_actual = getattr(request.user, 'funcionario', None)
    if not funcionario_actual:
        funcionario_actual = Funcionario.objects.filter(user=request.user).first()
    if not funcionario_actual and not es_admin:
        if delegacion_activa:
            funcionario_actual = Funcionario.objects.filter(id_delegacion=delegacion_activa, activo=True).first()
        if not funcionario_actual:
            funcionario_actual = Funcionario.objects.filter(activo=True).first()

    # Si es admin, puede asignar a cualquier funcionario ordenado alfabéticamente
    funcionarios = Funcionario.objects.filter(activo=True).order_by('nombre')
    items_metas = ItemMeta.objects.filter(estado='Activo').order_by('nombre')

    # El tipo de gestión debe ser acorde al cargo del funcionario (o todos si es admin)
    tipos = obtener_tipos_por_cargo(request.user)

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
        item_evaluacion = request.POST.get('item_evaluacion', '').strip()
        estado = request.POST.get('estado', 'Pendiente')

        # Determinar funcionario y responsable según rol:
        # Si es admin: puede escoger el funcionario de la lista.
        # Si no es admin: se auto-asigna a sí mismo obligatoriamente.
        if es_admin:
            id_funcionario_post = request.POST.get('id_funcionario')
            responsable_nombre = request.POST.get('responsable', '').strip()
            funcionario_obj = None
            if id_funcionario_post:
                funcionario_obj = Funcionario.objects.filter(pk=id_funcionario_post).first()
            if not funcionario_obj and responsable_nombre:
                funcionario_obj = Funcionario.objects.filter(nombre__iexact=responsable_nombre).first()
                if not funcionario_obj:
                    funcionario_obj = Funcionario.objects.filter(nombre__icontains=responsable_nombre).first()
            if not funcionario_obj:
                funcionario_obj = funcionario_actual or funcionarios.first()
            responsable_nombre = funcionario_obj.nombre
        else:
            funcionario_obj = funcionario_actual or funcionarios.first()
            responsable_nombre = funcionario_obj.nombre

        # Datos solicitante / vecino
        solicitante = request.POST.get('solicitante', '').strip() or request.POST.get('contacto', '').strip()
        rut_solicitante = request.POST.get('rut_solicitante', '').strip()
        telefono = request.POST.get('telefono', '').strip()
        correo = request.POST.get('correo', '').strip()
        direccion = request.POST.get('direccion', '').strip()
        territorio = request.POST.get('territorio', '').strip()

        # Registro o actualización automática en tabla Vecino
        vecino_obj = None
        if rut_solicitante:
            vecino_obj = Vecino.objects.filter(rut__iexact=rut_solicitante).first()
            if not vecino_obj:
                # Normalizar si existe sin puntos
                rut_limpio = rut_solicitante.replace('.', '').replace(' ', '').upper()
                for v in Vecino.objects.all():
                    if v.rut.replace('.', '').replace(' ', '').upper() == rut_limpio:
                        vecino_obj = v
                        break
            if not vecino_obj:
                vecino_obj = Vecino.objects.create(
                    rut=rut_solicitante,
                    nombre=solicitante or 'Vecino Sin Nombre',
                    telefono=telefono,
                    correo=correo,
                    direccion=direccion,
                    territorio=territorio,
                )
            else:
                cambio_vecino = False
                if solicitante and not vecino_obj.nombre:
                    vecino_obj.nombre = solicitante
                    cambio_vecino = True
                if telefono and not vecino_obj.telefono:
                    vecino_obj.telefono = telefono
                    cambio_vecino = True
                if correo and not vecino_obj.correo:
                    vecino_obj.correo = correo
                    cambio_vecino = True
                if direccion and not vecino_obj.direccion:
                    vecino_obj.direccion = direccion
                    cambio_vecino = True
                if territorio and not vecino_obj.territorio:
                    vecino_obj.territorio = territorio
                    cambio_vecino = True
                if cambio_vecino:
                    vecino_obj.save()

        # Clasificación temática (TipoAtencion exclusivo)
        id_tipo = request.POST.get('id_tipo')
        id_subatencion = request.POST.get('id_subatencion')
        tipo_obj = TipoAtencion.objects.filter(pk=id_tipo).first() if id_tipo else None
        # Si no se seleccionó tipo, asignar el primer tipo autorizado
        if not tipo_obj and tipos.exists():
            tipo_obj = tipos.first()
        sub_obj = SubAtencion.objects.filter(pk=id_subatencion).first() if id_subatencion else None

        # Derivación a Tubo de Trabajo
        ingreso_tubo = request.POST.get('ingreso_tubo') in ('SI', 'si', 'on', 'true', '1')
        fecha_compromiso = request.POST.get('fecha_compromiso') or None
        area_apoyo = request.POST.get('area_apoyo', '').strip()

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

        if not solicitud or not accion or not item_evaluacion:
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
                'es_admin': es_admin,
                'funcionario_actual': funcionario_actual,
                'valores': request.POST,
            })

        # Crear actividad/gestión unificada
        actividad = Actividad.objects.create(
            usuario_creador=request.user if request.user.is_authenticated else None,
            id_funcionario=funcionario_obj,
            id_delegacion=delegacion_activa or (funcionario_obj.id_delegacion if funcionario_obj else None),
            id_vecino=vecino_obj,
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
        'es_admin': es_admin,
        'funcionario_actual': funcionario_actual,
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