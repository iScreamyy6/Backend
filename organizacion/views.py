from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Delegacion, Funcionario


def lista_unidades(request):
    q = request.GET.get('q', '').strip()
    unidades = Delegacion.objects.all()
    if q:
        unidades = unidades.filter(
            Q(nombre__icontains=q) | Q(ambito__icontains=q) | Q(responsable__icontains=q)
        )
    contexto = {
        'unidades': unidades,
        'cantidad': unidades.count()
    }
    return render(request, 'organizacion/lista_unidades.html', contexto)


def detalle_unidad(request, unidad_id):
    unidad = get_object_or_404(Delegacion, id=unidad_id)
    return render(request, 'organizacion/detalle_unidad.html', {'unidad': unidad})


def lista_personas(request):
    q = request.GET.get('q', '').strip()
    personas = Funcionario.objects.select_related('delegacion').all()
    if q:
        personas = personas.filter(
            Q(nombre__icontains=q) | Q(cargo__icontains=q) | Q(delegacion__nombre__icontains=q)
        )
    contexto = {
        'personas': personas,
        'cantidad': personas.count()
    }
    return render(request, 'organizacion/lista_personas.html', contexto)


def detalle_persona(request, persona_id):
    persona = get_object_or_404(Funcionario.objects.select_related('delegacion'), id=persona_id)
    return render(request, 'organizacion/detalle_persona.html', {'persona': persona})