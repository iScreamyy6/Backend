from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Compromiso


def lista_compromisos(request):
    q = request.GET.get('q', '').strip()
    compromisos = Compromiso.objects.all()
    if q:
        compromisos = compromisos.filter(
            Q(actividad__icontains=q) |
            Q(solicitante__icontains=q) |
            Q(responsable__icontains=q) |
            Q(territorio__icontains=q)
        )

    contexto = {
        'compromisos': compromisos,
        'cantidad': compromisos.count()
    }
    return render(request, 'agenda/lista_compromisos.html', contexto)


def detalle_compromiso(request, compromiso_id):
    compromiso = get_object_or_404(Compromiso, pk=compromiso_id)
    return render(request, 'agenda/detalle_compromiso.html', {'compromiso': compromiso})


def formulario_compromiso(request):
    return render(request, 'agenda/formulario_compromiso.html', {})


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