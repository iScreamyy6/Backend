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


def resumen_agenda(request):
    compromisos = Compromiso.objects.all()
    total = compromisos.count()

    col_ingresados = compromisos.filter(estado='INGRESADO')
    col_pendientes = compromisos.filter(estado='PENDIENTE')
    col_proceso = compromisos.filter(estado='EN PROCESO')
    col_realizados = compromisos.filter(estado='REALIZADO')

    total_realizados = col_realizados.count()
    tasa_resolucion = round((total_realizados / total * 100) if total > 0 else 0, 1)

    contexto = {
        'total': total,
        'col_ingresados': col_ingresados,
        'col_pendientes': col_pendientes,
        'col_proceso': col_proceso,
        'col_realizados': col_realizados,
        'total_realizados': total_realizados,
        'total_proceso': col_proceso.count(),
        'total_pendientes': col_pendientes.count(),
        'tasa_resolucion': tasa_resolucion
    }
    return render(request, 'agenda/resumen_agenda.html', contexto)