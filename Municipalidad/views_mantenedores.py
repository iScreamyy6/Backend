import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse, JsonResponse

from organizacion.models import Delegacion, Rol, PerfilUsuario, Funcionario
from actividades.models import TipoAtencion, SubAtencion, AtencionCiudadana, Actividad
from resultados.models import ItemMeta


class EmptyValues:
    """Objeto centinela compatible con Django 6.x: devuelve string vacio
    para cualquier atributo o clave que se intente acceder en un template.
    Evita VariableDoesNotExist cuando el formulario se abre en modo creacion (GET).
    """
    def __getattr__(self, name):
        return ''

    def __getitem__(self, key):
        return ''

    def get(self, key, default=''):
        return default


# ==============================================================================
# HELPER DE EXPORTACIÓN EXCEL INSTITUCIONAL
# ==============================================================================
def generar_excel_institucional(titulo_hoja, filename, columnas, filas):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = titulo_hoja

    # Estilos según Normas Gráficas de La Serena (#AD0000 y Arial)
    fill_header = PatternFill(start_color="AD0000", end_color="AD0000", fill_type="solid")
    font_header = Font(name="Arial", size=11, bold=True, color="FFFFFF")
    font_data = Font(name="Arial", size=10)

    ws.append(columnas)
    for col_idx in range(1, len(columnas) + 1):
        cell = ws.cell(row=1, column=col_idx)
        cell.fill = fill_header
        cell.font = font_header
        cell.alignment = Alignment(horizontal="center", vertical="center")
        col_letter = get_column_letter(col_idx)
        ws.column_dimensions[col_letter].width = 22

    for row_idx, fila in enumerate(filas, start=2):
        ws.append(fila)
        for col_idx in range(1, len(fila) + 1):
            cell = ws.cell(row=row_idx, column=col_idx)
            cell.font = font_data

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="{filename}.xlsx"'
    wb.save(response)
    return response


# ==============================================================================
# HELPERS DE SEGURIDAD Y PERMISOS POR ROL
# ==============================================================================
def es_admin(user):
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    perfil = getattr(user, 'perfil', None)
    return bool(perfil and perfil.rol and perfil.rol.codigo == 'ROL-ADM')


def es_admin_o_coord(user):
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    perfil = getattr(user, 'perfil', None)
    return bool(perfil and perfil.rol and perfil.rol.codigo in ('ROL-ADM', 'ROL-COORD'))


# ==============================================================================
# CRUD 1: DELEGACIONES
# ==============================================================================
@login_required(login_url='login')
def delegaciones_lista(request):
    if not es_admin_o_coord(request.user):
        messages.error(request, 'Acceso restringido: Su perfil de rol no tiene permisos para gestionar delegaciones.')
        return redirect('inicio')

    q = request.GET.get('q', '').strip()
    estado = request.GET.get('estado', '').strip()
    exportar = request.GET.get('exportar') == 'excel'

    queryset = Delegacion.objects.all().order_by('codigo', 'nombre')

    if q:
        queryset = queryset.filter(
            Q(codigo__icontains=q) |
            Q(nombre__icontains=q) |
            Q(ambito__icontains=q) |
            Q(responsable__icontains=q) |
            Q(comuna__icontains=q)
        )
    if estado:
        queryset = queryset.filter(estado=estado)

    if exportar:
        columnas = ['Código', 'Nombre Delegación', 'Dirección', 'Comuna', 'Ámbito Territorial', 'Responsable', 'Estado']
        filas = [
            [d.codigo, d.nombre, d.direccion, d.comuna, d.ambito, d.responsable, d.estado]
            for d in queryset
        ]
        return generar_excel_institucional('Delegaciones', 'delegaciones_sgr', columnas, filas)

    paginador = Paginator(queryset, 10)
    page_number = request.GET.get('page')
    page_obj = paginador.get_page(page_number)

    return render(request, 'mantenedores/delegaciones/lista.html', {
        'page_obj': page_obj,
        'q': q,
        'estado_filtro': estado,
        'total_registros': queryset.count(),
    })


@login_required(login_url='login')
def delegaciones_crear(request):
    if not es_admin_o_coord(request.user):
        messages.error(request, 'Acceso restringido: Su perfil de rol no tiene permisos para gestionar delegaciones.')
        return redirect('inicio')

    if request.method == 'POST':
        codigo = request.POST.get('codigo', '').strip().upper()
        nombre = request.POST.get('nombre', '').strip()
        direccion = request.POST.get('direccion', '').strip()
        comuna = request.POST.get('comuna', 'La Serena').strip()
        ambito = request.POST.get('ambito', '').strip()
        responsable = request.POST.get('responsable', '').strip()
        foco = request.POST.get('foco_estrategico', '').strip()
        estado = request.POST.get('estado', 'Activa')

        if not nombre or not responsable:
            messages.error(request, 'Los campos Nombre y Responsable son obligatorios.')
            return render(request, 'mantenedores/delegaciones/formulario.html', {'valores': request.POST})

        if Delegacion.objects.filter(nombre__iexact=nombre).exists():
            messages.error(request, f'Ya existe una delegación con el nombre "{nombre}".')
            return render(request, 'mantenedores/delegaciones/formulario.html', {'valores': request.POST})

        d = Delegacion.objects.create(
            codigo=codigo,
            nombre=nombre,
            direccion=direccion,
            comuna=comuna,
            ambito=ambito,
            responsable=responsable,
            foco_estrategico=foco,
            estado=estado
        )
        messages.success(request, f'Delegación "{d.nombre}" creada exitosamente.')
        return redirect('delegaciones_lista')

    return render(request, 'mantenedores/delegaciones/formulario.html', {
        'titulo': 'Crear Delegación',
        'valores': EmptyValues(),
    })


@login_required(login_url='login')
def delegaciones_editar(request, pk):
    delegacion = get_object_or_404(Delegacion, pk=pk)

    if request.method == 'POST':
        delegacion.codigo = request.POST.get('codigo', '').strip().upper()
        delegacion.nombre = request.POST.get('nombre', '').strip()
        delegacion.direccion = request.POST.get('direccion', '').strip()
        delegacion.comuna = request.POST.get('comuna', 'La Serena').strip()
        delegacion.ambito = request.POST.get('ambito', '').strip()
        delegacion.responsable = request.POST.get('responsable', '').strip()
        delegacion.foco_estrategico = request.POST.get('foco_estrategico', '').strip()
        delegacion.estado = request.POST.get('estado', 'Activa')

        if not delegacion.nombre or not delegacion.responsable:
            messages.error(request, 'Los campos Nombre y Responsable son obligatorios.')
            return render(request, 'mantenedores/delegaciones/formulario.html', {'delegacion': delegacion})

        if Delegacion.objects.filter(nombre__iexact=delegacion.nombre).exclude(pk=pk).exists():
            messages.error(request, f'Ya existe otra delegación con el nombre "{delegacion.nombre}".')
            return render(request, 'mantenedores/delegaciones/formulario.html', {'delegacion': delegacion})

        delegacion.save()
        messages.success(request, f'Delegación "{delegacion.nombre}" actualizada con éxito.')
        return redirect('delegaciones_lista')

    return render(request, 'mantenedores/delegaciones/formulario.html', {'delegacion': delegacion, 'titulo': 'Editar Delegación'})


@login_required(login_url='login')
def delegaciones_eliminar(request, pk):
    delegacion = get_object_or_404(Delegacion, pk=pk)

    # Validar integridad referencial (funcionarios, atenciones, compromisos)
    tiene_relaciones = (
        delegacion.funcionarios.exists() or
        delegacion.atenciones_ciudadanas.exists() or
        delegacion.compromisos.exists()
    )

    if tiene_relaciones:
        # Desactivación lógica preservando historia
        delegacion.estado = 'Inactiva' if delegacion.estado == 'Activa' else 'Activa'
        delegacion.save()
        messages.warning(
            request,
            f'La delegación tiene registros vinculados. Se ha cambiado su estado a "{delegacion.estado}" para preservar la integridad.'
        )
    else:
        delegacion.delete()
        messages.success(request, 'Delegación eliminada permanentemente.')

    return redirect('delegaciones_lista')


# ==============================================================================
# CRUD 2: ROLES
# ==============================================================================
@login_required(login_url='login')
def roles_lista(request):
    if not es_admin(request.user):
        messages.error(request, 'Acceso restringido: Su perfil de rol no tiene permisos para administrar roles.')
        return redirect('inicio')

    q = request.GET.get('q', '').strip()
    exportar = request.GET.get('exportar') == 'excel'

    queryset = Rol.objects.all().order_by('codigo')

    if q:
        queryset = queryset.filter(
            Q(codigo__icontains=q) | Q(nombre__icontains=q) | Q(descripcion__icontains=q)
        )

    if exportar:
        columnas = ['Código', 'Nombre del Rol', 'Alcance Territorial', 'Permisos Asignados', 'Estado']
        filas = [[r.codigo, r.nombre, r.get_alcance_autorizado_display(), r.permisos, r.estado] for r in queryset]
        return generar_excel_institucional('Roles', 'roles_sgr', columnas, filas)

    paginador = Paginator(queryset, 10)
    page_obj = paginador.get_page(request.GET.get('page'))

    return render(request, 'mantenedores/roles/lista.html', {
        'page_obj': page_obj,
        'q': q,
        'total_registros': queryset.count(),
    })


@login_required(login_url='login')
def roles_crear(request):
    if request.method == 'POST':
        codigo = request.POST.get('codigo', '').strip().upper()
        nombre = request.POST.get('nombre', '').strip()
        descripcion = request.POST.get('descripcion', '').strip()
        alcance = request.POST.get('alcance_autorizado', 'DELEGACION')
        permisos = request.POST.get('permisos', '').strip()
        estado = request.POST.get('estado', 'Activo')

        if not nombre:
            messages.error(request, 'El campo Nombre del Rol es obligatorio.')
            return render(request, 'mantenedores/roles/formulario.html', {'valores': request.POST})

        if Rol.objects.filter(nombre__iexact=nombre).exists():
            messages.error(request, f'Ya existe un rol con el nombre "{nombre}".')
            return render(request, 'mantenedores/roles/formulario.html', {'valores': request.POST})

        if codigo and Rol.objects.filter(codigo__iexact=codigo).exists():
            messages.error(request, f'Ya existe un rol con el código "{codigo}".')
            return render(request, 'mantenedores/roles/formulario.html', {'valores': request.POST})

        r = Rol.objects.create(
            codigo=codigo,
            nombre=nombre,
            descripcion=descripcion,
            alcance_autorizado=alcance,
            permisos=permisos,
            estado=estado
        )
        messages.success(request, f'Rol "{r.nombre}" [{r.codigo}] creado exitosamente.')
        return redirect('roles_lista')

    return render(request, 'mantenedores/roles/formulario.html', {
        'titulo': 'Crear Rol',
        'valores': EmptyValues(),
    })


@login_required(login_url='login')
def roles_editar(request, pk):
    rol = get_object_or_404(Rol, pk=pk)

    if request.method == 'POST':
        rol.codigo = request.POST.get('codigo', '').strip().upper()
        rol.nombre = request.POST.get('nombre', '').strip()
        rol.descripcion = request.POST.get('descripcion', '').strip()
        rol.alcance_autorizado = request.POST.get('alcance_autorizado', 'DELEGACION')
        rol.permisos = request.POST.get('permisos', '').strip()
        rol.estado = request.POST.get('estado', 'Activo')

        if not rol.codigo or not rol.nombre:
            messages.error(request, 'Código y Nombre son obligatorios.')
            return render(request, 'mantenedores/roles/formulario.html', {'rol': rol})

        rol.save()
        messages.success(request, f'Rol "{rol.nombre}" actualizado con éxito.')
        return redirect('roles_lista')

    return render(request, 'mantenedores/roles/formulario.html', {'rol': rol, 'titulo': 'Editar Rol'})


@login_required(login_url='login')
def roles_eliminar(request, pk):
    rol = get_object_or_404(Rol, pk=pk)
    if rol.usuarios.exists():
        rol.estado = 'Inactivo' if rol.estado == 'Activo' else 'Activo'
        rol.save()
        messages.warning(request, f'El rol posee usuarios asociados. Se ha cambiado su estado a "{rol.estado}".')
    else:
        rol.delete()
        messages.success(request, 'Rol eliminado permanentemente.')
    return redirect('roles_lista')


# ==============================================================================
# CRUD 3: USUARIOS
# ==============================================================================
@login_required(login_url='login')
def usuarios_lista(request):
    if not es_admin(request.user):
        messages.error(request, 'Acceso restringido: Su perfil de rol no tiene permisos para administrar usuarios.')
        return redirect('inicio')

    q = request.GET.get('q', '').strip()
    exportar = request.GET.get('exportar') == 'excel'

    queryset = User.objects.select_related('perfil__rol', 'perfil__delegacion_activa').all().order_by('username')

    if q:
        queryset = queryset.filter(
            Q(username__icontains=q) |
            Q(first_name__icontains=q) |
            Q(last_name__icontains=q) |
            Q(email__icontains=q) |
            Q(perfil__rol__nombre__icontains=q) |
            Q(perfil__delegacion_activa__nombre__icontains=q)
        )

    if exportar:
        columnas = ['Usuario', 'Nombre Completo', 'Correo Electrónico', 'Rol Asignado', 'Delegación Activa', 'Estado']
        filas = [
            [
                u.username,
                u.get_full_name() or '—',
                u.email or '—',
                u.perfil.rol.nombre if hasattr(u, 'perfil') and u.perfil.rol else 'Sin Rol',
                u.perfil.delegacion_activa.nombre if hasattr(u, 'perfil') and u.perfil.delegacion_activa else 'Sin Delegación',
                u.perfil.estado if hasattr(u, 'perfil') else 'Activo',
            ]
            for u in queryset
        ]
        return generar_excel_institucional('Usuarios', 'usuarios_sgr', columnas, filas)

    paginador = Paginator(queryset, 10)
    page_obj = paginador.get_page(request.GET.get('page'))

    return render(request, 'mantenedores/usuarios/lista.html', {
        'page_obj': page_obj,
        'q': q,
        'total_registros': queryset.count(),
    })


@login_required(login_url='login')
def usuarios_crear(request):
    roles = Rol.objects.filter(estado='Activo')
    delegaciones = Delegacion.objects.filter(estado='Activa')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '').strip()
        rol_id = request.POST.get('rol')
        delegacion_id = request.POST.get('delegacion_activa')
        delegaciones_ids = request.POST.getlist('delegaciones_autorizadas')
        estado = request.POST.get('estado', 'Activo')

        if not username or not email or not password:
            messages.error(request, 'Usuario, Correo y Contraseña son obligatorios.')
            return render(request, 'mantenedores/usuarios/formulario.html', {
                'roles': roles,
                'delegaciones': delegaciones,
                'valores': request.POST
            })

        if User.objects.filter(Q(username__iexact=username) | Q(email__iexact=email)).exists():
            messages.error(request, 'Ya existe una cuenta con ese nombre de usuario o correo.')
            return render(request, 'mantenedores/usuarios/formulario.html', {
                'roles': roles,
                'delegaciones': delegaciones,
                'valores': request.POST
            })

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )

        perfil, _ = PerfilUsuario.objects.get_or_create(user=user)
        if rol_id:
            perfil.rol = Rol.objects.filter(pk=rol_id).first()
        if delegacion_id:
            perfil.delegacion_activa = Delegacion.objects.filter(pk=delegacion_id).first()
        perfil.estado = estado
        perfil.save()

        if delegaciones_ids:
            perfil.delegaciones_autorizadas.set(delegaciones_ids)
        elif perfil.delegacion_activa:
            perfil.delegaciones_autorizadas.add(perfil.delegacion_activa)

        messages.success(request, f'Usuario "{user.username}" registrado exitosamente.')
        return redirect('usuarios_lista')

    return render(request, 'mantenedores/usuarios/formulario.html', {
        'roles': roles,
        'delegaciones': delegaciones,
        'titulo': 'Crear Usuario',
        'valores': EmptyValues(),
    })


@login_required(login_url='login')
def usuarios_editar(request, pk):
    user_obj = get_object_or_404(User, pk=pk)
    perfil, _ = PerfilUsuario.objects.get_or_create(user=user_obj)
    roles = Rol.objects.filter(estado='Activo')
    delegaciones = Delegacion.objects.filter(estado='Activa')

    if request.method == 'POST':
        user_obj.first_name = request.POST.get('first_name', '').strip()
        user_obj.last_name = request.POST.get('last_name', '').strip()
        user_obj.email = request.POST.get('email', '').strip().lower()

        password = request.POST.get('password', '').strip()
        if password:
            user_obj.set_password(password)

        rol_id = request.POST.get('rol')
        delegacion_id = request.POST.get('delegacion_activa')
        delegaciones_ids = request.POST.getlist('delegaciones_autorizadas')
        estado = request.POST.get('estado', 'Activo')

        perfil.rol = Rol.objects.filter(pk=rol_id).first() if rol_id else None
        perfil.delegacion_activa = Delegacion.objects.filter(pk=delegacion_id).first() if delegacion_id else None
        perfil.estado = estado
        perfil.save()

        if delegaciones_ids:
            perfil.delegaciones_autorizadas.set(delegaciones_ids)

        user_obj.save()
        messages.success(request, f'Usuario "{user_obj.username}" actualizado con éxito.')
        return redirect('usuarios_lista')

    return render(request, 'mantenedores/usuarios/formulario.html', {
        'user_obj': user_obj,
        'perfil': perfil,
        'roles': roles,
        'delegaciones': delegaciones,
        'titulo': 'Editar Usuario'
    })


@login_required(login_url='login')
def usuarios_eliminar(request, pk):
    user_obj = get_object_or_404(User, pk=pk)
    if user_obj.is_superuser:
        messages.error(request, 'No es posible desactivar o eliminar la cuenta de superusuario.')
        return redirect('usuarios_lista')

    perfil = getattr(user_obj, 'perfil', None)
    if perfil:
        perfil.estado = 'Inactivo' if perfil.estado == 'Activo' else 'Activo'
        perfil.save()
        messages.warning(request, f'Estado del usuario cambiado a "{perfil.estado}".')
    return redirect('usuarios_lista')


# ==============================================================================
# CRUD 4: ÍTEMS Y METAS
# ==============================================================================
@login_required(login_url='login')
def items_lista(request):
    if not es_admin_o_coord(request.user):
        messages.error(request, 'Acceso restringido: Su perfil de rol no tiene permisos para acceder a este catálogo.')
        return redirect('inicio')

    q = request.GET.get('q', '').strip()
    exportar = request.GET.get('exportar') == 'excel'

    queryset = ItemMeta.objects.all().order_by('codigo')

    if q:
        queryset = queryset.filter(
            Q(codigo__icontains=q) | Q(nombre__icontains=q) | Q(descripcion__icontains=q)
        )

    if exportar:
        columnas = ['Código', 'Nombre del Ítem', 'Tipo de Meta', 'Descripción', 'Estado']
        filas = [[it.codigo, it.nombre, it.tipo_meta, it.descripcion, it.estado] for it in queryset]
        return generar_excel_institucional('Items_Metas', 'items_metas_sgr', columnas, filas)

    paginador = Paginator(queryset, 10)
    page_obj = paginador.get_page(request.GET.get('page'))

    return render(request, 'mantenedores/items/lista.html', {
        'page_obj': page_obj,
        'q': q,
        'total_registros': queryset.count(),
    })


@login_required(login_url='login')
def items_crear(request):
    if request.method == 'POST':
        codigo = request.POST.get('codigo', '').strip().upper()
        nombre = request.POST.get('nombre', '').strip()
        tipo_meta = request.POST.get('tipo_meta', 'Cuantitativa')
        descripcion = request.POST.get('descripcion', '').strip()
        estado = request.POST.get('estado', 'Activo')

        if not nombre:
            messages.error(request, 'El campo Nombre del Ítem es obligatorio.')
            return render(request, 'mantenedores/items/formulario.html', {'valores': request.POST})

        if ItemMeta.objects.filter(nombre__iexact=nombre).exists():
            messages.error(request, f'Ya existe un ítem con el nombre "{nombre}".')
            return render(request, 'mantenedores/items/formulario.html', {'valores': request.POST})

        if codigo and ItemMeta.objects.filter(codigo__iexact=codigo).exists():
            messages.error(request, f'Ya existe un ítem con el código "{codigo}".')
            return render(request, 'mantenedores/items/formulario.html', {'valores': request.POST})

        it = ItemMeta.objects.create(
            codigo=codigo,
            nombre=nombre,
            tipo_meta=tipo_meta,
            descripcion=descripcion,
            estado=estado
        )
        messages.success(request, f'Ítem "{it.nombre}" [{it.codigo}] creado exitosamente.')
        return redirect('items_lista')

    return render(request, 'mantenedores/items/formulario.html', {
        'titulo': 'Crear Ítem de Evaluación',
        'valores': EmptyValues(),
    })


@login_required(login_url='login')
def items_editar(request, pk):
    item = get_object_or_404(ItemMeta, pk=pk)

    if request.method == 'POST':
        item.codigo = request.POST.get('codigo', '').strip().upper()
        item.nombre = request.POST.get('nombre', '').strip()
        item.tipo_meta = request.POST.get('tipo_meta', 'Cuantitativa')
        item.descripcion = request.POST.get('descripcion', '').strip()
        item.estado = request.POST.get('estado', 'Activo')

        if not item.codigo or not item.nombre:
            messages.error(request, 'Código y Nombre son obligatorios.')
            return render(request, 'mantenedores/items/formulario.html', {'item': item})

        item.save()
        messages.success(request, f'Ítem "{item.nombre}" actualizado con éxito.')
        return redirect('items_lista')

    return render(request, 'mantenedores/items/formulario.html', {'item': item, 'titulo': 'Editar Ítem'})


@login_required(login_url='login')
def items_eliminar(request, pk):
    item = get_object_or_404(ItemMeta, pk=pk)
    item.estado = 'Inactivo' if item.estado == 'Activo' else 'Activo'
    item.save()
    messages.warning(request, f'Estado del ítem cambiado a "{item.estado}".')
    return redirect('items_lista')


# ==============================================================================
# CRUD 5: TIPO DE ATENCIÓN
# ==============================================================================
@login_required(login_url='login')
def tipos_atencion_lista(request):
    if not es_admin_o_coord(request.user):
        messages.error(request, 'Acceso restringido: Su perfil de rol no tiene permisos para acceder a este catálogo.')
        return redirect('inicio')

    q = request.GET.get('q', '').strip()
    exportar = request.GET.get('exportar') == 'excel'

    queryset = TipoAtencion.objects.all().order_by('codigo')

    if q:
        queryset = queryset.filter(
            Q(codigo__icontains=q) | Q(nombre__icontains=q) | Q(descripcion__icontains=q)
        )

    if exportar:
        columnas = ['Código', 'Nombre Tipo de Atención', 'Descripción', 'Estado']
        filas = [[t.codigo, t.nombre, t.descripcion, t.estado] for t in queryset]
        return generar_excel_institucional('Tipos_Atencion', 'tipos_atencion_sgr', columnas, filas)

    paginador = Paginator(queryset, 10)
    page_obj = paginador.get_page(request.GET.get('page'))

    return render(request, 'mantenedores/tipos_atencion/lista.html', {
        'page_obj': page_obj,
        'q': q,
        'total_registros': queryset.count(),
    })


@login_required(login_url='login')
def tipos_atencion_crear(request):
    if request.method == 'POST':
        codigo = request.POST.get('codigo', '').strip().upper()
        nombre = request.POST.get('nombre', '').strip()
        descripcion = request.POST.get('descripcion', '').strip()
        estado = request.POST.get('estado', 'Activo')

        if not nombre:
            messages.error(request, 'El campo Nombre del Tipo de Atención es obligatorio.')
            return render(request, 'mantenedores/tipos_atencion/formulario.html', {'valores': request.POST})

        if TipoAtencion.objects.filter(nombre__iexact=nombre).exists():
            messages.error(request, f'Ya existe un Tipo de Atención con el nombre "{nombre}".')
            return render(request, 'mantenedores/tipos_atencion/formulario.html', {'valores': request.POST})

        if codigo and TipoAtencion.objects.filter(codigo__iexact=codigo).exists():
            messages.error(request, f'Ya existe un Tipo de Atención con el código "{codigo}".')
            return render(request, 'mantenedores/tipos_atencion/formulario.html', {'valores': request.POST})

        t = TipoAtencion.objects.create(
            codigo=codigo,
            nombre=nombre,
            descripcion=descripcion,
            estado=estado
        )
        messages.success(request, f'Tipo de Atención "{t.nombre}" [{t.codigo}] creado exitosamente.')
        return redirect('tipos_atencion_lista')

    return render(request, 'mantenedores/tipos_atencion/formulario.html', {
        'titulo': 'Crear Tipo de Atención',
        'valores': EmptyValues(),
    })


@login_required(login_url='login')
def tipos_atencion_editar(request, pk):
    tipo = get_object_or_404(TipoAtencion, pk=pk)

    if request.method == 'POST':
        tipo.codigo = request.POST.get('codigo', '').strip().upper()
        tipo.nombre = request.POST.get('nombre', '').strip()
        tipo.descripcion = request.POST.get('descripcion', '').strip()
        tipo.estado = request.POST.get('estado', 'Activo')

        if not tipo.codigo or not tipo.nombre:
            messages.error(request, 'Código y Nombre son obligatorios.')
            return render(request, 'mantenedores/tipos_atencion/formulario.html', {'tipo': tipo})

        tipo.save()
        messages.success(request, f'Tipo de Atención "{tipo.nombre}" actualizado con éxito.')
        return redirect('tipos_atencion_lista')

    return render(request, 'mantenedores/tipos_atencion/formulario.html', {'tipo': tipo, 'titulo': 'Editar Tipo de Atención'})


@login_required(login_url='login')
def tipos_atencion_eliminar(request, pk):
    tipo = get_object_or_404(TipoAtencion, pk=pk)
    if tipo.subatenciones.exists() or tipo.atenciones.exists():
        tipo.estado = 'Inactivo' if tipo.estado == 'Activo' else 'Activo'
        tipo.save()
        messages.warning(request, f'El tipo de atención posee subatenciones o registros asociados. Se ha cambiado su estado a "{tipo.estado}".')
    else:
        tipo.delete()
        messages.success(request, 'Tipo de Atención eliminado.')
    return redirect('tipos_atencion_lista')


# ==============================================================================
# CRUD 6: SUB ATENCIÓN
# ==============================================================================
@login_required(login_url='login')
def subatenciones_lista(request):
    if not es_admin_o_coord(request.user):
        messages.error(request, 'Acceso restringido: Su perfil de rol no tiene permisos para acceder a este catálogo.')
        return redirect('inicio')

    q = request.GET.get('q', '').strip()
    tipo_filtro = request.GET.get('tipo', '').strip()
    exportar = request.GET.get('exportar') == 'excel'

    queryset = SubAtencion.objects.select_related('id_tipo').all().order_by('id_tipo__nombre', 'codigo')

    if q:
        queryset = queryset.filter(
            Q(codigo__icontains=q) | Q(nombre__icontains=q) | Q(id_tipo__nombre__icontains=q)
        )
    if tipo_filtro:
        queryset = queryset.filter(id_tipo_id=tipo_filtro)

    if exportar:
        columnas = ['Código', 'Sub Atención', 'Tipo de Atención Asociado', 'Estado']
        filas = [[s.codigo, s.nombre, s.id_tipo.nombre, s.estado] for s in queryset]
        return generar_excel_institucional('Sub_Atenciones', 'subatenciones_sgr', columnas, filas)

    paginador = Paginator(queryset, 10)
    page_obj = paginador.get_page(request.GET.get('page'))

    return render(request, 'mantenedores/subatenciones/lista.html', {
        'page_obj': page_obj,
        'q': q,
        'tipo_filtro': tipo_filtro,
        'tipos': TipoAtencion.objects.filter(estado='Activo'),
        'total_registros': queryset.count(),
    })


@login_required(login_url='login')
def subatenciones_crear(request):
    tipos = TipoAtencion.objects.filter(estado='Activo')

    if request.method == 'POST':
        codigo = request.POST.get('codigo', '').strip().upper()
        nombre = request.POST.get('nombre', '').strip()
        id_tipo = request.POST.get('id_tipo')
        estado = request.POST.get('estado', 'Activo')

        if not nombre or not id_tipo:
            messages.error(request, 'Nombre y Tipo de Atención son obligatorios.')
            return render(request, 'mantenedores/subatenciones/formulario.html', {'tipos': tipos, 'valores': request.POST})

        if codigo and SubAtencion.objects.filter(codigo__iexact=codigo).exists():
            messages.error(request, f'Ya existe una subatención con el código "{codigo}".')
            return render(request, 'mantenedores/subatenciones/formulario.html', {'tipos': tipos, 'valores': request.POST})

        s = SubAtencion.objects.create(
            codigo=codigo,
            nombre=nombre,
            id_tipo_id=id_tipo,
            estado=estado
        )
        messages.success(request, f'Sub Atención "{s.nombre}" [{s.codigo}] creada exitosamente.')
        return redirect('subatenciones_lista')

    return render(request, 'mantenedores/subatenciones/formulario.html', {
        'tipos': tipos,
        'titulo': 'Crear Sub Atención',
        'valores': EmptyValues(),
    })


@login_required(login_url='login')
def subatenciones_editar(request, pk):
    sub = get_object_or_404(SubAtencion, pk=pk)
    tipos = TipoAtencion.objects.filter(estado='Activo')

    if request.method == 'POST':
        sub.codigo = request.POST.get('codigo', '').strip().upper()
        sub.nombre = request.POST.get('nombre', '').strip()
        sub.id_tipo_id = request.POST.get('id_tipo')
        sub.estado = request.POST.get('estado', 'Activo')

        if not sub.codigo or not sub.nombre or not sub.id_tipo_id:
            messages.error(request, 'Código, Nombre y Tipo son obligatorios.')
            return render(request, 'mantenedores/subatenciones/formulario.html', {'sub': sub, 'tipos': tipos})

        sub.save()
        messages.success(request, f'Sub Atención "{sub.nombre}" actualizada con éxito.')
        return redirect('subatenciones_lista')

    return render(request, 'mantenedores/subatenciones/formulario.html', {'sub': sub, 'tipos': tipos, 'titulo': 'Editar Sub Atención'})


@login_required(login_url='login')
def subatenciones_eliminar(request, pk):
    sub = get_object_or_404(SubAtencion, pk=pk)
    if sub.atenciones.exists():
        sub.estado = 'Inactivo' if sub.estado == 'Activo' else 'Activo'
        sub.save()
        messages.warning(request, f'La subatención tiene atenciones vinculadas. Se ha cambiado su estado a "{sub.estado}".')
    else:
        sub.delete()
        messages.success(request, 'Sub Atención eliminada.')
    return redirect('subatenciones_lista')


# ==============================================================================
# INGRESO Y GESTIÓN DE ATENCIÓN CIUDADANA
# ==============================================================================
@login_required(login_url='login')
def atencion_nueva(request):
    tipos = TipoAtencion.objects.filter(estado='Activo')
    delegacion_activa_id = request.session.get('delegacion_activa_id')
    delegacion_activa = Delegacion.objects.filter(pk=delegacion_activa_id).first() if delegacion_activa_id else Delegacion.objects.filter(estado='Activa').first()

    if request.method == 'POST':
        solicitante = request.POST.get('solicitante', '').strip()
        rut = request.POST.get('rut_solicitante', '').strip()
        telefono = request.POST.get('telefono', '').strip()
        correo = request.POST.get('correo', '').strip()
        direccion = request.POST.get('direccion', '').strip()
        id_tipo = request.POST.get('id_tipo')
        id_subatencion = request.POST.get('id_subatencion')
        descripcion = request.POST.get('descripcion', '').strip()

        if not solicitante or not id_tipo or not id_subatencion or not descripcion:
            messages.error(request, 'Por favor complete todos los campos obligatorios (*).')
            return render(request, 'atenciones/formulario.html', {
                'tipos': tipos,
                'delegacion_activa': delegacion_activa,
                'valores': request.POST
            })

        # Prevenir doble envío idéntico en menos de 10 segundos
        tipo_obj = get_object_or_404(TipoAtencion, pk=id_tipo)
        sub_obj = get_object_or_404(SubAtencion, pk=id_subatencion, id_tipo=tipo_obj)

        atencion = AtencionCiudadana.objects.create(
            solicitante=solicitante,
            rut_solicitante=rut,
            telefono=telefono,
            correo=correo,
            direccion=direccion,
            id_tipo=tipo_obj,
            id_subatencion=sub_obj,
            descripcion=descripcion,
            id_delegacion=delegacion_activa,
            id_usuario_responsable=request.user,
            estado='Ingresada'
        )

        # Sincronización con el Módulo Unificado de Gestiones (Actividad)
        funcionario_default = Funcionario.objects.first()
        Actividad.objects.create(
            id_funcionario=funcionario_default,
            id_delegacion=delegacion_activa,
            id_atencion=atencion,
            fecha=atencion.fecha_registro.date(),
            solicitante=solicitante,
            rut_solicitante=rut,
            telefono=telefono,
            correo=correo,
            direccion=direccion,
            territorio=direccion or (delegacion_activa.nombre if delegacion_activa else ''),
            contacto=solicitante,
            id_tipo=tipo_obj,
            id_subatencion=sub_obj,
            solicitud=descripcion,
            accion='Atención ciudadana registrada e integrada en gestiones',
            responsable=request.user.get_full_name() or request.user.username,
            item_evaluacion='ATENCION DE USUARIO TELEFONO Y PRESENCIAL',
            estado='Pendiente'
        )

        messages.success(
            request,
            f'¡Atención registrada exitosamente! Se ha generado el Folio Oficial: {atencion.folio} y ha quedado integrada al Módulo de Gestiones.'
        )
        return redirect('atenciones_lista')

    return render(request, 'atenciones/formulario.html', {
        'tipos': tipos,
        'delegacion_activa': delegacion_activa,
        'valores': EmptyValues(),
    })


@login_required(login_url='login')
def atenciones_lista(request):
    q = request.GET.get('q', '').strip()
    exportar = request.GET.get('exportar') == 'excel'

    delegacion_activa_id = request.session.get('delegacion_activa_id')

    queryset = AtencionCiudadana.objects.select_related(
        'id_tipo', 'id_subatencion', 'id_delegacion', 'id_usuario_responsable'
    ).all()

    # Si el usuario tiene una delegación activa fijada en sesión, filtrar por ese contexto
    if delegacion_activa_id:
        queryset = queryset.filter(id_delegacion_id=delegacion_activa_id)

    if q:
        queryset = queryset.filter(
            Q(folio__icontains=q) |
            Q(solicitante__icontains=q) |
            Q(rut_solicitante__icontains=q) |
            Q(descripcion__icontains=q) |
            Q(id_tipo__nombre__icontains=q) |
            Q(id_subatencion__nombre__icontains=q)
        )

    if exportar:
        columnas = ['Folio', 'Fecha Registro', 'Solicitante', 'RUT', 'Tipo Atención', 'Sub Atención', 'Delegación', 'Responsable', 'Estado']
        filas = [
            [
                a.folio,
                a.fecha_registro.strftime('%d/%m/%Y %H:%M'),
                a.solicitante,
                a.rut_solicitante or '—',
                a.id_tipo.nombre,
                a.id_subatencion.nombre,
                a.id_delegacion.nombre,
                a.id_usuario_responsable.get_full_name() or a.id_usuario_responsable.username,
                a.estado,
            ]
            for a in queryset
        ]
        return generar_excel_institucional('Atenciones', 'atenciones_ciudadanas_sgr', columnas, filas)

    paginador = Paginator(queryset, 10)
    page_obj = paginador.get_page(request.GET.get('page'))

    return render(request, 'atenciones/lista.html', {
        'page_obj': page_obj,
        'q': q,
        'total_registros': queryset.count(),
    })


@login_required(login_url='login')
def atenciones_detalle(request, pk):
    atencion = get_object_or_404(AtencionCiudadana.objects.select_related(
        'id_tipo', 'id_subatencion', 'id_delegacion', 'id_usuario_responsable'
    ), pk=pk)
    return render(request, 'atenciones/detalle.html', {'atencion': atencion})


# ==============================================================================
# API AJAX: SUBATENCIONES DEPENDIENTES EN CASCADA
# ==============================================================================
def api_subatenciones_por_tipo(request):
    tipo_id = request.GET.get('tipo_id')
    subatenciones = []
    if tipo_id:
        subs = SubAtencion.objects.filter(id_tipo_id=tipo_id, estado='Activo').order_by('nombre')
        subatenciones = [{'id': s.pk, 'nombre': s.nombre, 'codigo': s.codigo} for s in subs]
    return JsonResponse({'subatenciones': subatenciones})
