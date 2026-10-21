from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone

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
    actividades = Actividad.objects.select_related('id_funcionario').all()
    if q:
        actividades = actividades.filter(
            Q(codigo__icontains=q) |
            Q(solicitud__icontains=q) |
            Q(responsable__icontains=q) |
            Q(accion__icontains=q) |
            Q(item_evaluacion__icontains=q)
        )

    contexto = {
        'actividades': actividades,
        'cantidad': actividades.count(),
        'q': q,
    }
    return render(request, 'actividades/lista_actividades.html', contexto)


def detalle_actividad(request, actividad_id):
    actividad = get_object_or_404(Actividad.objects.select_related('id_funcionario'), pk=actividad_id)
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

    ultimo = Actividad.objects.order_by('-id_actividad').first()
    siguiente_id = (ultimo.id_actividad + 1) if ultimo else 1
    codigo_sugerido = f"GES-{siguiente_id:05d}"
    hoy = timezone.now().date()
    codigo_evi_sugerido = f"EVI-{hoy.strftime('%Y%m%d')}-{siguiente_id:04d}"

    if request.method == 'POST':
        fecha = request.POST.get('fecha') or hoy
        solicitud = request.POST.get('solicitud', '').strip()
        accion = request.POST.get('accion', '').strip()
        responsable_nombre = request.POST.get('responsable', '').strip()
        item_evaluacion = request.POST.get('item_evaluacion', '').strip()
        estado = request.POST.get('estado', 'Pendiente')
        contacto = request.POST.get('contacto', '').strip()
        telefono = request.POST.get('telefono', '').strip()
        ingreso_tubo = request.POST.get('ingreso_tubo') == 'SI'

        if not solicitud or not accion or not responsable_nombre or not item_evaluacion:
            messages.error(request, 'Por favor complete todos los campos obligatorios marcados con (*).')
            return render(request, 'actividades/formulario_actividad.html', {
                'funcionarios': funcionarios,
                'items_metas': items_metas,
                'delegacion_activa': delegacion_activa,
                'codigo_sugerido': codigo_sugerido,
                'codigo_evi_sugerido': codigo_evi_sugerido,
                'valores': request.POST,
            })

        funcionario_obj = Funcionario.objects.filter(nombre__iexact=responsable_nombre).first()
        if not funcionario_obj:
            funcionario_obj = Funcionario.objects.filter(nombre__icontains=responsable_nombre).first()
        if not funcionario_obj:
            funcionario_obj = funcionarios.first()

        actividad = Actividad.objects.create(
            id_funcionario=funcionario_obj,
            fecha=fecha,
            solicitud=solicitud,
            accion=accion,
            responsable=responsable_nombre,
            item_evaluacion=item_evaluacion,
            estado=estado,
            contacto=contacto,
            telefono=telefono,
            ingreso_tubo=ingreso_tubo,
        )

        if ingreso_tubo:
            Compromiso.objects.create(
                id_delegacion=delegacion_activa or funcionario_obj.id_delegacion,
                id_responsable=funcionario_obj,
                fecha_solicitud=fecha,
                actividad=f"[Derivado de {actividad.codigo}] {solicitud}",
                tipo='EXT',
                solicitante=contacto or 'Vecino / Terreno',
                responsable=responsable_nombre,
                estado='INGRESADO',
                observaciones=f"Gestión realizada: {accion}. Contacto: {telefono or 'N/A'}"
            )

        messages.success(
            request,
            f'¡Gestión guardada exitosamente! Se ha asignado el Código de Gestión: {actividad.codigo} y Evidencia: {actividad.codigo_evidencia}.'
            + (' (Se derivó automáticamente al Tubo de Trabajo).' if ingreso_tubo else '')
        )
        return redirect('actividades:lista_actividades')

    return render(request, 'actividades/formulario_actividad.html', {
        'funcionarios': funcionarios,
        'items_metas': items_metas,
        'delegacion_activa': delegacion_activa,
        'codigo_sugerido': codigo_sugerido,
        'codigo_evi_sugerido': codigo_evi_sugerido,
        'hoy': hoy.strftime('%Y-%m-%d'),
        'valores': EmptyValues(),
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

        if ingreso_tubo:
            Compromiso.objects.create(
                id_delegacion=delegacion_activa or funcionario_obj.id_delegacion,
                id_responsable=funcionario_obj,
                fecha_solicitud=fecha_ingreso,
                actividad=f"[Caso Social {gestion.codigo}] {sub_obj.nombre} para {usuario}",
                tipo='EXT',
                solicitante=usuario,
                responsable=funcionario_obj.nombre,
                estado='INGRESADO',
                observaciones=f"Detalle: {observaciones[:150]}. Requiere visita: {'Sí' if requiere_visita else 'No'}"
            )

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