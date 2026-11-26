from organizacion.models import Delegacion, PerfilUsuario, Funcionario


class EmptyValues:
    """Objeto centinela compatible con Django 6.x: devuelve string vacío
    para cualquier atributo o clave que se intente acceder en un template.
    Evita VariableDoesNotExist cuando un formulario se abre en modo edición o creación sin valores previos.
    """
    def __getattr__(self, name):
        return ''

    def __getitem__(self, key):
        return ''

    def get(self, key, default=''):
        return default


class ObjetoTodasDelegaciones:
    """Objeto centinela para representar el ámbito global 'Todas las Delegaciones' (Comunal)."""
    pk = 'TODAS'
    id = 0
    id_delegacion = 0
    codigo = 'COMUNAL'
    nombre = 'Todas las Delegaciones'
    estado = 'Activa'
    es_todas = True

    def __str__(self):
        return self.nombre

    def __int__(self):
        return 0

    def __bool__(self):
        return True

    def __eq__(self, other):
        if isinstance(other, ObjetoTodasDelegaciones):
            return True
        if other in ('TODAS', 'todas', 0, '0'):
            return True
        return False


def delegacion_context(request):
    if not request.user.is_authenticated:
        return {
            'delegacion_activa': None,
            'delegaciones_disponibles': Delegacion.objects.none(),
            'puede_cambiar_delegacion': False,
            'es_todas_delegaciones': False,
            'usuario_perfil': None,
            'rol_usuario': None,
            'valores': EmptyValues(),
        }

    perfil = getattr(request.user, 'perfil', None)
    if not perfil:
        perfil, _ = PerfilUsuario.objects.get_or_create(user=request.user)

    # Determinar delegaciones autorizadas según perfil
    es_admin = bool(
        request.user.is_superuser or
        request.user.groups.filter(name='Administrador').exists() or
        (perfil.rol and perfil.rol.codigo == 'ROL-ADM')
    )
    es_super = bool(
        es_admin or
        request.user.groups.filter(name='Supervisor').exists() or
        (perfil.rol and perfil.rol.codigo in ('ROL-COORD', 'ROL-DEL', 'ROL-VERIF'))
    )
    es_adminis = request.user.is_authenticated

    if es_admin:
        perfil_tier_nombre = 'Administrador'
    elif es_super:
        perfil_tier_nombre = 'Supervisor'
    else:
        perfil_tier_nombre = 'Administrativo'

    # REGLA ESTRICTA DE DELEGACIÓN:
    # - Administrador: Puede tener alcance COMUNAL y ver todas o alternar entre todas las activas.
    # - Supervisores/Verificadores, Delegados y Administrativos: SOLO ven su delegación correspondiente (su delegacion_activa o delegaciones_autorizadas).
    if es_admin and perfil.rol and perfil.rol.alcance_autorizado == 'COMUNAL':
        delegaciones_disponibles = Delegacion.objects.filter(estado='Activa')
    elif perfil.delegaciones_autorizadas.exists():
        delegaciones_disponibles = perfil.delegaciones_autorizadas.filter(estado='Activa')
    elif perfil.delegacion_activa and perfil.delegacion_activa.estado == 'Activa':
        delegaciones_disponibles = Delegacion.objects.filter(pk=perfil.delegacion_activa.pk, estado='Activa')
    else:
        # Fallback a delegación asignada en ficha de Funcionario si existe
        func_obj = getattr(request.user, 'funcionario', None)
        if not func_obj:
            func_obj = Funcionario.objects.filter(user=request.user).first()
        if func_obj and func_obj.id_delegacion and func_obj.id_delegacion.estado == 'Activa':
            delegaciones_disponibles = Delegacion.objects.filter(pk=func_obj.id_delegacion.pk)
        elif es_admin:
            delegaciones_disponibles = Delegacion.objects.filter(estado='Activa')
        else:
            primera_activa = Delegacion.objects.filter(estado='Activa').first()
            delegaciones_disponibles = Delegacion.objects.filter(pk=primera_activa.pk) if primera_activa else Delegacion.objects.none()

    delegacion_activa_id = request.session.get('delegacion_activa_id')
    # Solo Administradores con alcance Comunal o superusuarios pueden operar en modo 'TODAS'
    es_todas = str(delegacion_activa_id).strip().upper() in ('TODAS', '0') if es_admin else False
    delegacion_activa = None

    if es_todas:
        delegacion_activa = ObjetoTodasDelegaciones()
    elif delegacion_activa_id:
        delegacion_activa = delegaciones_disponibles.filter(pk=delegacion_activa_id).first()

    if not delegacion_activa and not es_todas:
        if perfil.delegacion_activa and delegaciones_disponibles.filter(pk=perfil.delegacion_activa.pk).exists():
            delegacion_activa = perfil.delegacion_activa
        else:
            delegacion_activa = delegaciones_disponibles.first()
        if delegacion_activa:
            request.session['delegacion_activa_id'] = delegacion_activa.pk

    puede_cambiar = bool(
        es_admin or (delegaciones_disponibles.count() > 1)
    )

    grupo_principal = request.user.groups.first().name if request.user.groups.exists() else perfil_tier_nombre

    return {
        'delegacion_activa': delegacion_activa,
        'delegaciones_disponibles': delegaciones_disponibles,
        'puede_cambiar_delegacion': puede_cambiar,
        'es_todas_delegaciones': es_todas,
        'usuario_perfil': perfil,
        'rol_usuario': perfil.rol,
        'es_administrador': es_admin,
        'es_supervisor': es_super,
        'es_administrativo': es_adminis,
        'perfil_tier_nombre': perfil_tier_nombre,
        'grupo_usuario_nombre': grupo_principal,
        'valores': EmptyValues(),
    }
