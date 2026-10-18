from organizacion.models import Delegacion, PerfilUsuario


def delegacion_context(request):
    if not request.user.is_authenticated:
        return {
            'delegacion_activa': None,
            'delegaciones_disponibles': Delegacion.objects.none(),
            'puede_cambiar_delegacion': False,
            'usuario_perfil': None,
            'rol_usuario': None,
        }

    perfil = getattr(request.user, 'perfil', None)
    if not perfil:
        perfil, _ = PerfilUsuario.objects.get_or_create(user=request.user)

    # Determinar delegaciones autorizadas según perfil
    if perfil.rol and perfil.rol.alcance_autorizado == 'COMUNAL':
        delegaciones_disponibles = Delegacion.objects.filter(estado='Activa')
    elif perfil.delegaciones_autorizadas.exists():
        delegaciones_disponibles = perfil.delegaciones_autorizadas.filter(estado='Activa')
    else:
        delegaciones_disponibles = Delegacion.objects.filter(estado='Activa')

    delegacion_activa_id = request.session.get('delegacion_activa_id')
    delegacion_activa = None

    if delegacion_activa_id:
        delegacion_activa = Delegacion.objects.filter(pk=delegacion_activa_id, estado='Activa').first()

    if not delegacion_activa:
        if perfil.delegacion_activa and perfil.delegacion_activa.estado == 'Activa':
            delegacion_activa = perfil.delegacion_activa
        else:
            delegacion_activa = delegaciones_disponibles.first()
        if delegacion_activa:
            request.session['delegacion_activa_id'] = delegacion_activa.pk

    return {
        'delegacion_activa': delegacion_activa,
        'delegaciones_disponibles': delegaciones_disponibles,
        'puede_cambiar_delegacion': delegaciones_disponibles.count() > 1,
        'usuario_perfil': perfil,
        'rol_usuario': perfil.rol,
    }
