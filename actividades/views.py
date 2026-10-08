from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Actividad, Evidencia


def lista_actividades(request):
    q = request.GET.get('q', '').strip()
    actividades = Actividad.objects.all()
    if q:
        actividades = actividades.filter(
            Q(solicitud__icontains=q) |
            Q(responsable__icontains=q) |
            Q(accion__icontains=q) |
            Q(item_evaluacion__icontains=q)
        )

    contexto = {
        'actividades': actividades,
        'cantidad': actividades.count()
    }
    return render(request, 'actividades/lista_actividades.html', contexto)


def detalle_actividad(request, actividad_id):
    actividad = get_object_or_404(Actividad, pk=actividad_id)
    return render(request, 'actividades/detalle_actividad.html', {'actividad': actividad})


def formulario_actividad(request):
    return render(request, 'actividades/formulario_actividad.html', {})


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