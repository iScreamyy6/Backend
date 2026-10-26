from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone

from .models import Compromiso
from organizacion.models import Delegacion, Funcionario


class EmptyValues:
    def __getattr__(self, name):
        return ''
    def __getitem__(self, key):
        return ''
    def get(self, key, default=''):
        return default


def lista_compromisos(request):
    q = request.GET.get('q', '').strip()
    compromisos = Compromiso.objects.select_related('id_delegacion', 'id_responsable').all()
    if q:
        compromisos = compromisos.filter(
            Q(codigo__icontains=q) |
            Q(actividad__icontains=q) |
            Q(solicitante__icontains=q) |
            Q(responsable__icontains=q) |
            Q(territorio__icontains=q)
        )

    contexto = {
        'compromisos': compromisos,
        'cantidad': compromisos.count(),
        'q': q,
    }
    return render(request, 'agenda/lista_compromisos.html', contexto)


def detalle_compromiso(request, compromiso_id):
    compromiso = get_object_or_404(
        Compromiso.objects.select_related('id_delegacion', 'id_responsable'),
        pk=compromiso_id
    )
    return render(request, 'agenda/detalle_compromiso.html', {'compromiso': compromiso})


@login_required(login_url='login')
def formulario_compromiso(request):
    delegacion_activa_id = request.session.get('delegacion_activa_id')
    delegacion_activa = (
        Delegacion.objects.filter(pk=delegacion_activa_id).first()
        if delegacion_activa_id
        else Delegacion.objects.filter(estado='Activa').first()
    )
    funcionarios = Funcionario.objects.filter(activo=True).order_by('nombre')

    ultimo = Compromiso.objects.order_by('-id_compromiso').first()
    siguiente_id = (ultimo.id_compromiso + 1) if ultimo else 1
    codigo_sugerido = f"TUB-{siguiente_id:05d}"
    hoy = timezone.now().date()

    if request.method == 'POST':
        fecha_solicitud = request.POST.get('fecha_solicitud') or hoy
        tipo = request.POST.get('tipo', 'EXT')
        actividad = request.POST.get('actividad', '').strip()
        solicitante = request.POST.get('solicitante', '').strip()
        territorio = request.POST.get('territorio', '').strip()
        responsable_nombre = request.POST.get('responsable', '').strip()
        fecha_compromiso = request.POST.get('fecha_compromiso') or None
        area_apoyo = request.POST.get('area_apoyo', '').strip()
        estado = request.POST.get('estado', 'INGRESADO')
        observaciones = request.POST.get('observaciones', '').strip()

        if not actividad or not solicitante or not responsable_nombre or not fecha_compromiso:
            messages.error(request, 'Por favor complete todos los campos obligatorios (*).')
            return render(request, 'agenda/formulario_compromiso.html', {
                'funcionarios': funcionarios,
                'delegacion_activa': delegacion_activa,
                'codigo_sugerido': codigo_sugerido,
                'valores': request.POST,
            })

        funcionario_obj = Funcionario.objects.filter(nombre__iexact=responsable_nombre).first()
        if not funcionario_obj:
            funcionario_obj = Funcionario.objects.filter(nombre__icontains=responsable_nombre).first()

        compromiso = Compromiso.objects.create(
            usuario_creador=request.user if request.user.is_authenticated else None,
            id_delegacion=delegacion_activa or (funcionario_obj.id_delegacion if funcionario_obj else Delegacion.objects.first()),
            id_responsable=funcionario_obj,
            fecha_solicitud=fecha_solicitud,
            tipo=tipo,
            actividad=actividad,
            solicitante=solicitante,
            territorio=territorio,
            responsable=responsable_nombre,
            fecha_compromiso=fecha_compromiso,
            area_apoyo=area_apoyo,
            estado=estado,
            observaciones=observaciones,
        )

        messages.success(
            request,
            f'¡Compromiso ingresado exitosamente al Tubo de Trabajo! Código Oficial Asignado: {compromiso.codigo}.'
        )
        return redirect('agenda:lista_compromisos')

    return render(request, 'agenda/formulario_compromiso.html', {
        'funcionarios': funcionarios,
        'delegacion_activa': delegacion_activa,
        'codigo_sugerido': codigo_sugerido,
        'hoy': hoy.strftime('%Y-%m-%d'),
        'valores': EmptyValues(),
    })


def puede_mover_compromiso(user, compromiso):
    """
    Determina si un usuario puede mover o cambiar de estado un compromiso en el tablero Kanban.
    Regla de negocio:
    - Los Administradores (is_superuser o ROL-ADM / ROL-COORD) pueden mover cualquier actividad.
    - Los usuarios no-admin solo pueden mover sus propias actividades (creadas por ellos o donde son el responsable).
    - NO pueden mover actividades de otros funcionarios ni de otras delegaciones.
    """
    if not user.is_authenticated:
        return False

    # 1. Administrador General o Superusuario: Control total
    if user.is_superuser:
        return True
    perfil = getattr(user, 'perfil', None)
    rol_codigo = perfil.rol.codigo if (perfil and perfil.rol) else ''
    if rol_codigo in ('ROL-ADM', 'ROL-COORD'):
        return True

    # 2. Si el compromiso fue creado directamente por este usuario
    if hasattr(compromiso, 'usuario_creador') and compromiso.usuario_creador_id == user.pk:
        return True

    # 3. Si la actividad vinculada fue creada por este usuario
    if compromiso.id_actividad and hasattr(compromiso.id_actividad, 'usuario_creador') and compromiso.id_actividad.usuario_creador_id == user.pk:
        return True

    # 4. Si el usuario actual es el responsable asignado (por nombre o funcionario)
    user_nombres = {
        user.username.strip().lower(),
        user.get_full_name().strip().lower(),
        user.first_name.strip().lower(),
    }
    user_nombres.discard('')

    resp_text = (compromiso.responsable or '').strip().lower()
    resp_obj_name = (compromiso.id_responsable.nombre or '').strip().lower() if compromiso.id_responsable else ''

    for u_name in user_nombres:
        if u_name and (u_name == resp_text or u_name == resp_obj_name or u_name in resp_text or resp_text in u_name):
            return True

    return False


def resumen_agenda(request):
    delegacion_activa_id = request.session.get('delegacion_activa_id')
    user = request.user

    es_admin = user.is_authenticated and (
        user.is_superuser or (
            getattr(user, 'perfil', None) and getattr(user.perfil, 'rol', None) and user.perfil.rol.codigo in ('ROL-ADM', 'ROL-COORD')
        )
    )

    compromisos = Compromiso.objects.select_related(
        'id_delegacion', 'id_responsable', 'id_actividad', 'usuario_creador'
    ).all()

    # Si no es admin y tiene alcance por delegación, filtrar por su delegación activa
    if not es_admin and user.is_authenticated:
        perfil = getattr(user, 'perfil', None)
        alcance = perfil.rol.alcance_autorizado if (perfil and perfil.rol) else 'COMUNAL'
        if alcance == 'DELEGACION':
            del_id = delegacion_activa_id or (perfil.delegacion_activa_id if perfil.delegacion_activa else None)
            if del_id:
                compromisos = compromisos.filter(id_delegacion_id=del_id)

    # Convertir queryset a lista y evaluar permisos de movimiento por tarjeta
    lista_compromisos_eval = list(compromisos)
    for c in lista_compromisos_eval:
        c.puede_mover = puede_mover_compromiso(user, c)

    total = len(lista_compromisos_eval)

    col_ingresados = [c for c in lista_compromisos_eval if c.estado == 'INGRESADO']
    col_pendientes = [c for c in lista_compromisos_eval if c.estado == 'PENDIENTE']
    col_proceso = [c for c in lista_compromisos_eval if c.estado == 'EN PROCESO']
    col_realizados = [c for c in lista_compromisos_eval if c.estado == 'REALIZADO']

    total_realizados = len(col_realizados)
    tasa_resolucion = round((total_realizados / total * 100) if total > 0 else 0, 1)

    contexto = {
        'total': total,
        'col_ingresados': col_ingresados,
        'col_pendientes': col_pendientes,
        'col_proceso': col_proceso,
        'col_realizados': col_realizados,
        'total_realizados': total_realizados,
        'total_proceso': len(col_proceso),
        'total_pendientes': len(col_pendientes),
        'tasa_resolucion': tasa_resolucion,
        'es_admin': es_admin,
    }
    return render(request, 'agenda/resumen_agenda.html', contexto)


@login_required(login_url='login')
def cambiar_estado_compromiso(request, compromiso_id, nuevo_estado):
    compromiso = get_object_or_404(
        Compromiso.objects.select_related('id_responsable', 'id_actividad', 'usuario_creador'),
        pk=compromiso_id
    )

    # Validar permisos: no se pueden mover actividades de otros a menos que seas admin
    if not puede_mover_compromiso(request.user, compromiso):
        messages.error(
            request,
            f'Acceso restringido: No puedes mover la actividad {compromiso.codigo} porque está asignada a otro funcionario. Solo el responsable o un Administrador pueden moverla.'
        )
        return redirect('agenda:resumen_agenda')

    estados_validos = {'INGRESADO': 'Ingresado', 'PENDIENTE': 'Pendiente', 'EN PROCESO': 'En Proceso', 'REALIZADO': 'Realizado'}

    estado_upper = nuevo_estado.upper()
    if estado_upper in estados_validos:
        compromiso.estado = estado_upper
        compromiso.save(update_fields=['estado'])

        # Si está vinculado a una actividad y se concluye el compromiso, actualizar estado de la actividad
        if compromiso.id_actividad and estado_upper == 'REALIZADO':
            compromiso.id_actividad.estado = 'Realizado'
            compromiso.id_actividad.save(update_fields=['estado'])

        messages.success(request, f'Compromiso {compromiso.codigo} actualizado a: {estados_validos[estado_upper]}.')
    else:
        messages.error(request, 'Estado no válido.')

    return redirect('agenda:resumen_agenda')