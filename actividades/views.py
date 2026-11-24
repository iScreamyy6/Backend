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


class ValoresDict(dict):
    def __missing__(self, key):
        return ''
    def __getattr__(self, name):
        return self.get(name, '')


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


@login_required(login_url='login')
def lista_actividades(request):
    q = request.GET.get('q', '').strip()
    filtro = request.GET.get('filtro', 'todas').strip()

    # Excluir subgestiones del tablero general: solo se listan gestiones principales
    queryset = Actividad.objects.filter(id_gestion_padre__isnull=True).select_related(
        'id_funcionario', 'id_delegacion', 'id_tipo', 'id_subatencion', 'id_compromiso', 'id_vecino'
    ).prefetch_related('subgestiones').all()

    # ── Filtro por rol y delegación ─────────────────────────────────────────
    # - Administradores (ROL-ADM o Superusuario) pueden ver 'TODAS' o filtrar por cualquier delegación seleccionada.
    # - Supervisores/Verificadores, Delegados y Funcionarios: SOLO ven su delegación correspondiente asignada.
    if request.user.is_authenticated:
        try:
            perfil = request.user.perfil
            rol_codigo = perfil.rol.codigo if perfil.rol else ''
            alcance = perfil.rol.alcance_autorizado if perfil.rol else 'COMUNAL'
        except Exception:
            perfil = None
            rol_codigo = ''
            alcance = 'COMUNAL'

        es_admin_usuario = bool(
            request.user.is_superuser
            or request.user.groups.filter(name='Administrador').exists()
            or rol_codigo == 'ROL-ADM'
        )

        delegacion_activa_id = request.session.get('delegacion_activa_id')
        es_todas = (str(delegacion_activa_id).strip().upper() in ('TODAS', '0')) if es_admin_usuario else False

        if es_admin_usuario:
            if not es_todas and delegacion_activa_id:
                try:
                    queryset = queryset.filter(id_delegacion_id=int(delegacion_activa_id))
                except (ValueError, TypeError):
                    pass
        else:
            # Para supervisores, delegados y funcionarios: restringir siempre a su delegación correspondiente
            del_propia_id = None
            if perfil and perfil.delegacion_activa:
                del_propia_id = perfil.delegacion_activa_id
            elif perfil and perfil.delegaciones_autorizadas.exists():
                del_propia_id = perfil.delegaciones_autorizadas.first().pk
            else:
                func_rec = Funcionario.objects.filter(user=request.user).first()
                if func_rec and func_rec.id_delegacion:
                    del_propia_id = func_rec.id_delegacion_id

            if del_propia_id:
                queryset = queryset.filter(id_delegacion_id=del_propia_id)
            elif not es_todas and delegacion_activa_id:
                try:
                    queryset = queryset.filter(id_delegacion_id=int(delegacion_activa_id))
                except (ValueError, TypeError):
                    pass
    # ──────────────────────────────────────────────────────────────────────────

    # ── Filtro por usuario Administrativo: solo sus propias gestiones ────────
    if request.user.is_authenticated:
        es_admin_grp = (
            request.user.is_superuser
            or request.user.groups.filter(name='Administrador').exists()
        )
        es_supervisor_grp = (
            es_admin_grp
            or request.user.groups.filter(name='Supervisor').exists()
        )
        if not es_supervisor_grp:
            # Administrativo: filtrar solo gestiones propias (por funcionario o creador)
            funcionario_propio = Funcionario.objects.filter(user=request.user).first()
            q_propio = Q(usuario_creador=request.user)
            if funcionario_propio:
                q_propio |= Q(id_funcionario=funcionario_propio)
            queryset = queryset.filter(q_propio)
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
        alias_tipos = {
            'social': 'TIP-SOC',
            'territorial': 'TIP-TERR',
            'seguridad': 'TIP-SEG',
            'atencion': 'TIP-SOC',
        }
        codigo_filtro = alias_tipos.get(filtro.lower(), filtro)
        # Filtrar exactamente por el tipo seleccionado (por código o por ID)
        queryset = queryset.filter(Q(id_tipo__codigo__iexact=codigo_filtro) | Q(id_tipo_id__exact=codigo_filtro if str(codigo_filtro).isdigit() else 0))

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

    # Flag para el template: si es Administrativo, solo ve gestiones propias
    _es_admin_grp = (
        request.user.is_superuser
        or request.user.groups.filter(name='Administrador').exists()
    ) if request.user.is_authenticated else True
    _es_supervisor_grp = (
        _es_admin_grp
        or request.user.groups.filter(name='Supervisor').exists()
    ) if request.user.is_authenticated else True
    solo_propias = request.user.is_authenticated and not _es_supervisor_grp

    contexto = {
        'actividades': queryset,
        'cantidad': queryset.count(),
        'q': q,
        'filtro': filtro,
        'total_todas': total_todas,
        'total_tubo': total_tubo,
        'tipos_activos': tipos_activos,
        'conteo_por_tipo': conteo_por_tipo,
        'solo_propias': solo_propias,
    }
    return render(request, 'actividades/lista_actividades.html', contexto)



@login_required(login_url='login')
def detalle_actividad(request, actividad_id):
    actividad = get_object_or_404(
        Actividad.objects.select_related(
            'id_funcionario', 'id_delegacion', 'id_tipo', 'id_subatencion', 'id_compromiso', 'id_gestion_padre', 'id_vecino'
        ),
        pk=actividad_id
    )
    subgestiones = actividad.subgestiones.select_related(
        'id_funcionario', 'id_tipo', 'id_subatencion', 'id_vecino'
    ).order_by('fecha', 'id_actividad')

    return render(request, 'actividades/detalle_actividad.html', {
        'actividad': actividad,
        'subgestiones': subgestiones,
    })


@login_required(login_url='login')
def formulario_actividad(request):
    delegacion_activa_id = request.session.get('delegacion_activa_id')
    es_todas = str(delegacion_activa_id).strip().upper() in ('TODAS', '0')
    delegacion_activa = None
    if not es_todas and delegacion_activa_id:
        try:
            delegacion_activa = Delegacion.objects.filter(pk=int(delegacion_activa_id), estado='Activa').first()
        except (ValueError, TypeError):
            pass
    if not delegacion_activa:
        perfil_u = getattr(request.user, 'perfil', None)
        if perfil_u and perfil_u.delegacion_activa:
            delegacion_activa = perfil_u.delegacion_activa
        else:
            delegacion_activa = Delegacion.objects.filter(estado='Activa').first()

    es_admin = es_admin_usuario(request.user)
    
    # Obtener gestión padre si se está registrando una subgestión de seguimiento (por ID de Actividad, Gestión Social o Atención)
    padre_id = request.GET.get('padre_id') or request.POST.get('id_gestion_padre')
    padre_social_id = request.GET.get('padre_social_id')
    padre_atencion_id = request.GET.get('padre_atencion_id')

    gestion_padre = Actividad.objects.filter(pk=padre_id).first() if padre_id else None

    # Si se solicitó seguimiento desde un Caso Social
    if not gestion_padre and padre_social_id:
        soc_obj = GestionSocial.objects.filter(pk=padre_social_id).first()
        if soc_obj:
            gestion_padre = Actividad.objects.filter(id_gestion_social=soc_obj).first()
            if not gestion_padre and soc_obj.codigo:
                gestion_padre = Actividad.objects.filter(codigo=soc_obj.codigo).first()

    # Si se solicitó seguimiento desde una Atención Ciudadana
    if not gestion_padre and padre_atencion_id:
        atc_obj = AtencionCiudadana.objects.filter(pk=padre_atencion_id).first()
        if atc_obj:
            gestion_padre = Actividad.objects.filter(id_atencion=atc_obj).first()

    # Si la gestión padre ya es una subgestión, vincular directamente a la gestión padre raíz
    if gestion_padre and gestion_padre.id_gestion_padre:
        gestion_padre = gestion_padre.id_gestion_padre

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

    es_social_get = bool((request.GET.get('tipo') == 'social') or (gestion_padre and gestion_padre.es_gestion_social))
    tubo_get = bool(request.GET.get('tubo') == '1')

    if gestion_padre:
        num_sub = gestion_padre.subgestiones.count() + 1
        codigo_sugerido = f"{gestion_padre.codigo}-S{num_sub:02d}"
    else:
        ultimo = Actividad.objects.order_by('-id_actividad').first()
        siguiente_id = (ultimo.id_actividad + 1) if ultimo else 1
        prefijo_sugerido = "SOC" if es_social_get else "GES"
        codigo_sugerido = f"{prefijo_sugerido}-{siguiente_id:05d}"

    hoy = timezone.now().date()
    codigo_evi_sugerido = f"EVI-{hoy.strftime('%Y%m%d')}-{codigo_sugerido[-5:]}"

    if request.method == 'POST':
        fecha = request.POST.get('fecha') or hoy
        solicitud = request.POST.get('solicitud', '').strip()
        accion = request.POST.get('accion', '').strip()
        item_evaluacion = request.POST.get('item_evaluacion', '').strip()
        estado = request.POST.get('estado', 'Pendiente')

        # Determinar funcionario y responsable según rol
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
        if not tipo_obj and gestion_padre:
            tipo_obj = gestion_padre.id_tipo
        if not tipo_obj and tipos.exists():
            tipo_obj = tipos.first()
        sub_obj = SubAtencion.objects.filter(pk=id_subatencion).first() if id_subatencion else None

        # Derivación a Tubo de Trabajo
        ingreso_tubo = bool(request.POST.get('ingreso_tubo') in ('SI', 'si', 'on', 'true', '1'))
        fecha_compromiso = request.POST.get('fecha_compromiso') or None
        area_apoyo = request.POST.get('area_apoyo', '').strip()

        # Especialización Gestor Social (hereda si el padre es social)
        es_gestion_social = bool(request.POST.get('es_gestion_social') in ('SI', 'si', 'on', 'true', '1') or es_social_get)
        requiere_visita = bool(request.POST.get('requiere_visita') in ('SI', 'si', 'on', 'true', '1'))
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
                'gestion_padre': gestion_padre,
                'valores': request.POST,
            })

        # Crear actividad/gestión unificada (o subgestión si tiene gestión padre)
        actividad = Actividad.objects.create(
            usuario_creador=request.user if request.user.is_authenticated else None,
            id_funcionario=funcionario_obj,
            id_delegacion=delegacion_activa or (funcionario_obj.id_delegacion if funcionario_obj else None),
            id_gestion_padre=gestion_padre,
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

        if gestion_padre:
            msg = f'¡Subgestión de seguimiento guardada exitosamente! Se ha asignado Código {actividad.codigo} vinculada a la Gestión Principal {gestion_padre.codigo}.'
            if codigo_tubo_asignado:
                msg += f' Derivada al Tubo de Trabajo ({codigo_tubo_asignado}).'
            messages.success(request, msg)
            return redirect('actividades:detalle_actividad', actividad_id=gestion_padre.pk)

        msg = f'¡Gestión guardada exitosamente! Se ha asignado Código de Gestión: {actividad.codigo} y Evidencia: {actividad.codigo_evidencia}.'
        if codigo_tubo_asignado:
            msg += f' Además, fue derivada exitosamente al Tubo de Trabajo (Código: {codigo_tubo_asignado}) y ya se visualiza en el Tablero Kanban.'
        if imagen_file:
            msg += ' La imagen de evidencia fue adjuntada correctamente.'

        messages.success(request, msg)
        return redirect('actividades:lista_actividades')

    # Valores iniciales si viene de una gestión padre
    valores_render = EmptyValues()
    if gestion_padre:
        valores_render = ValoresDict({
            'solicitante': gestion_padre.solicitante or gestion_padre.contacto or '',
            'contacto': gestion_padre.contacto or gestion_padre.solicitante or '',
            'rut_solicitante': gestion_padre.rut_solicitante or '',
            'telefono': gestion_padre.telefono or '',
            'correo': gestion_padre.correo or '',
            'direccion': gestion_padre.direccion or '',
            'territorio': gestion_padre.territorio or '',
            'id_tipo': str(gestion_padre.id_tipo_id) if gestion_padre.id_tipo_id else '',
            'id_subatencion': str(gestion_padre.id_subatencion_id) if gestion_padre.id_subatencion_id else '',
            'item_evaluacion': gestion_padre.item_evaluacion or '',
            'responsable': gestion_padre.responsable or '',
        })

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
        'valores': valores_render,
        'es_admin': es_admin,
        'funcionario_actual': funcionario_actual,
        'gestion_padre': gestion_padre,
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
    es_todas = str(delegacion_activa_id).strip().upper() in ('TODAS', '0')
    delegacion_activa = None
    if not es_todas and delegacion_activa_id:
        try:
            delegacion_activa = Delegacion.objects.filter(pk=int(delegacion_activa_id), estado='Activa').first()
        except (ValueError, TypeError):
            pass
    if not delegacion_activa:
        perfil_u = getattr(request.user, 'perfil', None)
        if perfil_u and perfil_u.delegacion_activa:
            delegacion_activa = perfil_u.delegacion_activa
        else:
            delegacion_activa = Delegacion.objects.filter(estado='Activa').first()
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
    actividad = Actividad.objects.filter(id_gestion_social=gestion).first()
    if not actividad and gestion.codigo:
        actividad = Actividad.objects.filter(codigo=gestion.codigo).first()
    subgestiones = actividad.subgestiones.all().order_by('fecha', 'id_actividad') if actividad else []

    return render(request, 'actividades/detalle_social.html', {
        'gestion': gestion,
        'actividad': actividad,
        'subgestiones': subgestiones,
    })


def es_admin_o_supervisor(usuario):
    """Determina si el usuario tiene privilegios de Administrador o Supervisor/Coordinador."""
    if not usuario or not usuario.is_authenticated:
        return False, False
    es_admin = bool(
        usuario.is_superuser
        or usuario.groups.filter(name='Administrador').exists()
        or (hasattr(usuario, 'perfil') and usuario.perfil.rol and usuario.perfil.rol.codigo == 'ROL-ADM')
    )
    es_supervisor = bool(
        es_admin
        or usuario.groups.filter(name='Supervisor').exists()
        or (hasattr(usuario, 'perfil') and usuario.perfil.rol and usuario.perfil.rol.codigo in ('ROL-COORD', 'ROL-DEL'))
    )
    return es_admin, es_supervisor


def puede_modificar_evidencia(usuario, evidencia):
    """Determina si el usuario tiene permisos para subsanar o modificar una evidencia."""
    if not usuario or not usuario.is_authenticated:
        return False
    es_admin, es_supervisor = es_admin_o_supervisor(usuario)
    if es_admin or es_supervisor:
        return True
    actividad = evidencia.id_actividad
    if actividad and actividad.usuario_creador_id == usuario.id:
        return True
    func_user = Funcionario.objects.filter(user=usuario).first()
    if func_user:
        if evidencia.id_funcionario_id == func_user.id:
            return True
        if actividad and actividad.id_funcionario_id == func_user.id:
            return True
        if actividad and actividad.id_delegacion_id and func_user.id_delegacion_id == actividad.id_delegacion_id:
            return True
    # Por defecto, usuarios de la delegación activa en sesión
    return True


# ==============================================================================
# EVIDENCIAS
# ==============================================================================
@login_required(login_url='login')
def lista_evidencias(request):
    # Sincronización de seguridad: asegurar que todas las actividades tengan registro de Evidencia
    for act in Actividad.objects.filter(evidencias__isnull=True):
        act._sincronizar_evidencia()

    q = request.GET.get('q', '').strip()
    filtro_estado = request.GET.get('estado', 'todos').strip()
    filtro_tipo = request.GET.get('tipo', 'todos').strip()

    es_admin, es_supervisor = es_admin_o_supervisor(request.user)
    perfil = getattr(request.user, 'perfil', None)

    queryset = Evidencia.objects.select_related(
        'id_actividad', 'id_funcionario', 'id_actividad__id_delegacion', 'usuario_revisor'
    ).all()

    # Filtro por delegación y rol:
    # - Administradores pueden ver comunal (todas) o una delegación específica seleccionada.
    # - Supervisores/Verificadores y Delegados solo ven evidencias de su delegación asignada correspondiente.
    delegacion_activa_id = request.session.get('delegacion_activa_id')
    es_todas = (str(delegacion_activa_id).strip().upper() in ('TODAS', '0')) if es_admin else False

    if es_admin:
        if not es_todas and delegacion_activa_id:
            try:
                queryset = queryset.filter(id_actividad__id_delegacion_id=int(delegacion_activa_id))
            except (ValueError, TypeError):
                pass
    elif es_supervisor:
        del_id = None
        if perfil and perfil.delegacion_activa:
            del_id = perfil.delegacion_activa_id
        elif perfil and perfil.delegaciones_autorizadas.exists():
            del_id = perfil.delegaciones_autorizadas.first().pk
        if not del_id:
            func = Funcionario.objects.filter(user=request.user).first()
            if func and func.id_delegacion:
                del_id = func.id_delegacion_id
        if not del_id and not es_todas and delegacion_activa_id:
            try:
                del_id = int(delegacion_activa_id)
            except (ValueError, TypeError):
                pass
        if del_id:
            queryset = queryset.filter(id_actividad__id_delegacion_id=del_id)
    else:
        # Funcionario/Administrativo de línea: ve sólo sus gestiones/evidencias
        func_propio = Funcionario.objects.filter(user=request.user).first()
        q_propio = Q(id_actividad__usuario_creador=request.user)
        if func_propio:
            q_propio |= Q(id_funcionario=func_propio) | Q(id_actividad__id_funcionario=func_propio)
        queryset = queryset.filter(q_propio)

    # Métricas antes de filtros secundarios de tabla
    total_evidencias = queryset.count()
    aprobadas = queryset.filter(estado_validacion='Aprobada').count()
    en_revision = queryset.filter(estado_validacion__in=['En Revisión', 'Pendiente']).count()
    requieren_info = queryset.filter(estado_validacion__in=['Requiere Información', 'Corregir']).count()
    rechazadas = queryset.filter(estado_validacion='Rechazada').count()
    cualitativas = queryset.filter(tipo_impacto='Cualitativa').count()
    cuantitativas = queryset.filter(tipo_impacto='Cuantitativa').count()

    if q:
        queryset = queryset.filter(
            Q(codigo__icontains=q) |
            Q(id_actividad__codigo__icontains=q) |
            Q(id_actividad__solicitud__icontains=q) |
            Q(id_actividad__responsable__icontains=q) |
            Q(id_actividad__item_evaluacion__icontains=q) |
            Q(observacion__icontains=q)
        )

    if filtro_estado == 'aprobada':
        queryset = queryset.filter(estado_validacion='Aprobada')
    elif filtro_estado == 'revision':
        queryset = queryset.filter(estado_validacion__in=['En Revisión', 'Pendiente'])
    elif filtro_estado == 'informacion':
        queryset = queryset.filter(estado_validacion__in=['Requiere Información', 'Corregir'])
    elif filtro_estado == 'rechazada':
        queryset = queryset.filter(estado_validacion='Rechazada')

    if filtro_tipo == 'cuantitativa':
        queryset = queryset.filter(tipo_impacto='Cuantitativa')
    elif filtro_tipo == 'cualitativa':
        queryset = queryset.filter(tipo_impacto='Cualitativa')

    queryset = queryset.order_by('-fecha_carga', '-id_evidencia')

    contexto = {
        'evidencias': queryset,
        'total_evidencias': total_evidencias,
        'aprobadas': aprobadas,
        'en_revision': en_revision,
        'requieren_info': requieren_info,
        'rechazadas': rechazadas,
        'cualitativas': cualitativas,
        'cuantitativas': cuantitativas,
        'filtro_estado': filtro_estado,
        'filtro_tipo': filtro_tipo,
        'q': q,
        'puede_verificar': es_admin or es_supervisor,
        'es_admin': es_admin,
        'es_supervisor': es_supervisor,
    }
    return render(request, 'actividades/lista_evidencias.html', contexto)


@login_required(login_url='login')
def detalle_evidencia(request, evidencia_id):
    evidencia = get_object_or_404(
        Evidencia.objects.select_related(
            'id_actividad', 'id_funcionario', 'id_actividad__id_delegacion', 'usuario_revisor'
        ),
        pk=evidencia_id
    )
    actividad = evidencia.id_actividad

    es_admin, es_supervisor = es_admin_o_supervisor(request.user)
    puede_verificar = es_admin or es_supervisor
    puede_modificar = puede_modificar_evidencia(request.user, evidencia)
    esta_devuelta = evidencia.estado_validacion in ['Requiere Información', 'Corregir']

    if request.method == 'POST':
        accion = request.POST.get('accion', '').strip()
        dictamen = request.POST.get('dictamen', '').strip()

        # Flujo 1: Subsanación y sobreescritura por parte del funcionario (o supervisor/admin)
        if accion == 'subsanar' or (not dictamen and ('observacion_subsanacion' in request.POST or 'imagen_subsanacion' in request.FILES)):
            if not puede_modificar:
                messages.error(request, 'No tiene permisos para modificar esta evidencia.')
                return redirect('actividades:detalle_evidencia', evidencia_id=evidencia.pk)

            if evidencia.estado_validacion == 'Aprobada' and not (es_admin or es_supervisor):
                messages.error(request, 'La evidencia ya se encuentra aprobada y no requiere subsanación.')
                return redirect('actividades:detalle_evidencia', evidencia_id=evidencia.pk)

            observacion_sub = request.POST.get('observacion_subsanacion', '').strip()
            nueva_imagen = request.FILES.get('imagen_subsanacion') or request.FILES.get('imagen_evidencia')

            if not observacion_sub and not nueva_imagen:
                messages.warning(
                    request,
                    'Debe ingresar antecedentes complementarios o adjuntar una nueva imagen para subsanar la evidencia.'
                )
                return redirect('actividades:detalle_evidencia', evidencia_id=evidencia.pk)

            ahora = timezone.now()
            if nueva_imagen:
                evidencia.imagen = nueva_imagen
                evidencia.archivo_ruta = nueva_imagen.name

            if observacion_sub:
                nombre_autor = request.user.get_full_name() or request.user.username
                fecha_fmt = ahora.strftime('%d/%m/%Y %H:%M')
                nota = f"[Subsanado por {nombre_autor} - {fecha_fmt}]: {observacion_sub}"
                if evidencia.observacion:
                    evidencia.observacion = f"{evidencia.observacion}\n\n{nota}"
                else:
                    evidencia.observacion = nota

            evidencia.estado_validacion = 'En Revisión'
            evidencia.imagen_verificada = False
            evidencia.verificador_valido = False
            evidencia.save()

            if actividad:
                actividad.estado_evidencia = 'En Revisión'
                actividad.observacion_revision = evidencia.observacion
                actividad._skip_evidencia_auto = True
                actividad.save(update_fields=['estado_evidencia', 'observacion_revision'])

            messages.success(
                request,
                f'¡Evidencia {evidencia.codigo} sobreescrita y actualizada exitosamente! '
                f'Los nuevos antecedentes han sido enviados y la evidencia quedó en estado "En Revisión" para el dictamen del supervisor.'
            )
            return redirect('actividades:detalle_evidencia', evidencia_id=evidencia.pk)

        # Flujo 2: Dictamen formal del supervisor/auditor
        if not puede_verificar:
            messages.error(request, 'No tiene permisos de Administrador o Supervisor para dictaminar evidencias.')
            return redirect('actividades:detalle_evidencia', evidencia_id=evidencia.pk)

        tipo_impacto = request.POST.get('tipo_impacto', 'Cuantitativa').strip()
        observaciones = request.POST.get('observaciones', '').strip()
        imagen_verificada = bool(request.POST.get('imagen_verificada'))
        verificador_valido = bool(request.POST.get('verificador_valido'))

        # Normalizar valores
        if dictamen not in ['Aprobada', 'En Revisión', 'Requiere Información', 'Rechazada']:
            dictamen = 'En Revisión'
        if tipo_impacto not in ['Cuantitativa', 'Cualitativa']:
            tipo_impacto = 'Cuantitativa'

        if dictamen in ['Requiere Información', 'Rechazada'] and not observaciones:
            messages.warning(
                request,
                'Debe ingresar observaciones detalladas indicando qué antecedentes adicionales se requieren para continuar la revisión.'
                if dictamen == 'Requiere Información' else
                'Debe ingresar el motivo de auditoría por el cual se rechaza la evidencia.'
            )
            return render(request, 'actividades/detalle_evidencia.html', {
                'evidencia': evidencia,
                'actividad': actividad,
                'puede_verificar': puede_verificar,
                'puede_modificar': puede_modificar,
                'esta_devuelta': esta_devuelta,
                'es_admin': es_admin,
                'es_supervisor': es_supervisor,
            })

        ahora = timezone.now()
        evidencia.estado_validacion = dictamen
        evidencia.tipo_impacto = tipo_impacto
        evidencia.observacion = observaciones
        evidencia.imagen_verificada = imagen_verificada
        evidencia.verificador_valido = verificador_valido
        evidencia.fecha_revision = ahora
        evidencia.usuario_revisor = request.user
        evidencia.save()

        if actividad:
            actividad.estado_evidencia = dictamen
            actividad.tipo_impacto = tipo_impacto
            actividad.observacion_revision = observaciones
            actividad.fecha_revision = ahora
            actividad.usuario_revisor = request.user
            actividad._skip_evidencia_auto = True
            actividad.save(update_fields=[
                'estado_evidencia', 'tipo_impacto', 'observacion_revision', 'fecha_revision', 'usuario_revisor'
            ])

        if dictamen == 'Aprobada':
            if tipo_impacto == 'Cuantitativa':
                messages.success(
                    request,
                    f'Evidencia {evidencia.codigo} APROBADA exitosamente como CUANTITATIVA. '
                    f'La gestión ha quedado validada y pondera de inmediato en el porcentaje de metas.'
                )
            else:
                messages.success(
                    request,
                    f'Evidencia {evidencia.codigo} APROBADA como CUALITATIVA. '
                    f'La gestión queda registrada y validada para fines institucionales, sin ponderar en el porcentaje cuantitativo de metas.'
                )
        elif dictamen == 'Requiere Información':
            messages.warning(
                request,
                f'Se ha solicitado más información o evidencias para {evidencia.codigo}. '
                f'La evidencia ha sido devuelta al funcionario con las observaciones para su subsanación.'
            )
        elif dictamen == 'Rechazada':
            messages.error(
                request,
                f'La evidencia {evidencia.codigo} ha sido RECHAZADA. No es computable para el cumplimiento de metas.'
            )
        else:
            messages.info(
                request,
                f'La evidencia {evidencia.codigo} permanece En Revisión en la bandeja de auditoría.'
            )

        return redirect('actividades:detalle_evidencia', evidencia_id=evidencia.pk)

    return render(request, 'actividades/detalle_evidencia.html', {
        'evidencia': evidencia,
        'actividad': actividad,
        'puede_verificar': puede_verificar,
        'puede_modificar': puede_modificar,
        'esta_devuelta': esta_devuelta,
        'es_admin': es_admin,
        'es_supervisor': es_supervisor,
    })


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
    evidencia_devuelta = actividad.evidencias.filter(
        estado_validacion__in=['Requiere Información', 'Corregir']
    ).first()

    evidencia_id_param = request.POST.get('evidencia_id') or request.GET.get('evidencia_id')
    evidencia_objetivo = None
    if evidencia_id_param:
        evidencia_objetivo = actividad.evidencias.filter(pk=evidencia_id_param).first()
    if not evidencia_objetivo:
        evidencia_objetivo = evidencia_devuelta

    if request.method == 'POST':
        imagen_file = request.FILES.get('imagen_evidencia')
        observacion = request.POST.get('observacion_evidencia', '').strip()

        if not imagen_file and not observacion:
            messages.error(request, 'Debe seleccionar una imagen o ingresar observaciones para la evidencia.')
            return render(request, 'actividades/subir_evidencia.html', {
                'actividad': actividad,
                'evidencias': evidencias_existentes,
                'evidencia_devuelta': evidencia_devuelta,
                'evidencia_objetivo': evidencia_objetivo,
            })

        # Si existe una evidencia devuelta o especificada, SOBREESCRIBIRLA (no duplicar registros)
        if evidencia_objetivo:
            if imagen_file:
                evidencia_objetivo.imagen = imagen_file
                evidencia_objetivo.archivo_ruta = imagen_file.name

            if observacion:
                nombre_autor = request.user.get_full_name() or request.user.username
                fecha_str = timezone.now().strftime('%d/%m/%Y %H:%M')
                nota = f"[Subsanado por {nombre_autor} - {fecha_str}]: {observacion}"
                if evidencia_objetivo.observacion:
                    evidencia_objetivo.observacion = f"{evidencia_objetivo.observacion}\n\n{nota}"
                else:
                    evidencia_objetivo.observacion = nota

            evidencia_objetivo.estado_validacion = 'En Revisión'
            evidencia_objetivo.imagen_verificada = False
            evidencia_objetivo.verificador_valido = False
            evidencia_objetivo.save()

            actividad.estado_evidencia = 'En Revisión'
            actividad.observacion_revision = evidencia_objetivo.observacion
            actividad._skip_evidencia_auto = True
            actividad.save(update_fields=['estado_evidencia', 'observacion_revision'])

            messages.success(
                request,
                f'¡Evidencia {evidencia_objetivo.codigo} sobreescrita y actualizada exitosamente! '
                f'Ha regresado a la bandeja de auditoría en estado "En Revisión" para el supervisor.'
            )
            return redirect('actividades:detalle_evidencia', evidencia_id=evidencia_objetivo.pk)

        # Si no había evidencia previa devuelta y no se especificó sobreescritura:
        if not imagen_file:
            messages.error(request, 'Debe seleccionar una imagen para subir como evidencia.')
            return render(request, 'actividades/subir_evidencia.html', {
                'actividad': actividad,
                'evidencias': evidencias_existentes,
                'evidencia_devuelta': evidencia_devuelta,
                'evidencia_objetivo': evidencia_objetivo,
            })

        # Determinar código único para esta evidencia
        num_ev = evidencias_existentes.count() + 1
        codigo_ev = f"{actividad.codigo_evidencia or actividad.codigo}-EV{num_ev:02d}"
        if Evidencia.objects.filter(codigo=codigo_ev).exists():
            import uuid
            codigo_ev = f"{actividad.codigo}-{uuid.uuid4().hex[:6].upper()}"

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

        nueva_ev = Evidencia.objects.create(
            id_actividad=actividad,
            id_funcionario=funcionario_obj,
            codigo=codigo_ev,
            imagen=imagen_file,
            archivo_ruta=imagen_file.name,
            observacion=observacion,
            estado_validacion='En Revisión',
        )

        messages.success(
            request,
            f'¡Evidencia cargada correctamente para la gestión {actividad.codigo}! '
            f'Código de evidencia asignado: {codigo_ev}. Estado: En Revisión.'
        )
        return redirect('actividades:detalle_evidencia', evidencia_id=nueva_ev.pk)

    return render(request, 'actividades/subir_evidencia.html', {
        'actividad': actividad,
        'evidencias': evidencias_existentes,
        'evidencia_devuelta': evidencia_devuelta,
        'evidencia_objetivo': evidencia_objetivo,
    })

    return render(request, 'actividades/subir_evidencia.html', {
        'actividad': actividad,
        'evidencias': evidencias_existentes,
    })