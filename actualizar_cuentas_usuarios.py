"""
Script para sincronizar y conectar nombres de usuario y correos con el nombre de cada cuenta.
Asigna a cada funcionario su cuenta con su nombre de superhéroe y dominio @correo.cl.
Idempotente y seguro ante duplicados.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Municipalidad.settings')
django.setup()

from django.contrib.auth.models import User, Group
from organizacion.models import Funcionario, PerfilUsuario, Rol
from actividades.models import Actividad
from agenda.models import Compromiso

grp_admin = Group.objects.get(name='Administrador')
grp_super = Group.objects.get(name='Supervisor')
grp_adminis = Group.objects.get(name='Administrativo')

rol_adm = Rol.objects.filter(codigo='ROL-ADM').first()
rol_coord = Rol.objects.filter(codigo='ROL-COORD').first()
rol_del = Rol.objects.filter(codigo='ROL-DEL').first()
rol_ter = Rol.objects.filter(codigo='ROL-TER').first()
rol_ges = Rol.objects.filter(codigo='ROL-GES').first() or Rol.objects.filter(codigo='ROL-OPE').first()
rol_ope = Rol.objects.filter(codigo='ROL-OPE').first()
rol_dis = Rol.objects.filter(codigo='ROL-DIS').first()

# 1. Renombrar usuarios existentes
mapeo_existentes = {
    'operador_d02': {
        'new_username': 'acuaman',
        'email': 'acuaman@correo.cl',
        'first_name': 'Acuaman',
        'last_name': 'Territorial',
        'rol': rol_ter,
        'grupo': grp_adminis,
        'func_nombre': 'Acuaman',
    },
    'operador_d01': {
        'new_username': 'flash',
        'email': 'flash@correo.cl',
        'first_name': 'Flash',
        'last_name': 'Social',
        'rol': rol_ges,
        'grupo': grp_adminis,
        'func_nombre': 'Flash',
    },
    'delegado_d01': {
        'new_username': 'heman',
        'email': 'heman@correo.cl',
        'first_name': 'He-Man',
        'last_name': 'Delegado',
        'rol': rol_del,
        'grupo': grp_super,
        'func_nombre': 'He-Man',
    },
    'diserco': {
        'new_username': 'capitanamarvel',
        'email': 'capitanamarvel@correo.cl',
        'first_name': 'Capitana',
        'last_name': 'Marvel',
        'rol': rol_dis,
        'grupo': grp_adminis,
        'func_nombre': 'Capitana Marvel',
    },
}

for old_user, info in mapeo_existentes.items():
    target_username = info['new_username']
    u = User.objects.filter(username=old_user).first()
    existing_target = User.objects.filter(username=target_username).first()

    if u and existing_target and u.pk != existing_target.pk:
        # Si existen ambos, eliminar el antiguo o reasignar
        u.delete()
        u = existing_target
    elif not u:
        u = existing_target

    if not u:
        u = User.objects.create(username=target_username)

    u.username = target_username
    u.email = info['email']
    u.first_name = info['first_name']
    u.last_name = info['last_name']
    u.set_password('admin')
    u.save()

    u.groups.clear()
    u.groups.add(info['grupo'])

    f = Funcionario.objects.filter(nombre__icontains=info['func_nombre']).first()
    if f:
        f.user = u
        f.save()

    p, _ = PerfilUsuario.objects.get_or_create(user=u)
    p.rol = info['rol']
    if f and f.id_delegacion:
        p.delegacion_activa = f.id_delegacion
        p.delegaciones_autorizadas.add(f.id_delegacion)
    p.estado = 'Activo'
    p.save()
    print(f'[OK] Usuario sincronizado: {u.username} | {u.email} -> Funcionario: {f.nombre if f else "None"}')

# 2. Actualizar coordinador
u_coord = User.objects.filter(username='coordinador').first()
if u_coord:
    u_coord.email = 'coordinador@correo.cl'
    u_coord.set_password('admin')
    u_coord.save()
    print(f'[OK] Usuario coordinador actualizado: {u_coord.username} | {u_coord.email}')

# 3. Crear / vincular cuentas para los 4 funcionarios restantes
cuentas_nuevas = [
    {
        'username': 'spiderman',
        'email': 'spiderman@correo.cl',
        'first_name': 'Spider',
        'last_name': 'Man',
        'func_nombre': 'Spider-Man',
        'rol': rol_ter,
        'grupo': grp_adminis,
    },
    {
        'username': 'capitanamerica',
        'email': 'capitanamerica@correo.cl',
        'first_name': 'Capitán',
        'last_name': 'América',
        'func_nombre': 'Capitán América',
        'rol': rol_ges,
        'grupo': grp_adminis,
    },
    {
        'username': 'panteranegra',
        'email': 'panteranegra@correo.cl',
        'first_name': 'Pantera',
        'last_name': 'Negra',
        'func_nombre': 'Pantera Negra',
        'rol': rol_ope,
        'grupo': grp_adminis,
    },
    {
        'username': 'hulk',
        'email': 'hulk@correo.cl',
        'first_name': 'Hulk',
        'last_name': 'Social',
        'func_nombre': 'Hulk',
        'rol': rol_ges,
        'grupo': grp_adminis,
    },
]

for c in cuentas_nuevas:
    u, created = User.objects.get_or_create(username=c['username'])
    u.email = c['email']
    u.first_name = c['first_name']
    u.last_name = c['last_name']
    u.set_password('admin')
    u.is_active = True
    u.save()

    u.groups.clear()
    u.groups.add(c['grupo'])

    f = Funcionario.objects.filter(nombre__icontains=c['func_nombre'].split()[0]).first()
    if f:
        f.user = u
        f.save()

    p, _ = PerfilUsuario.objects.get_or_create(user=u)
    p.rol = c['rol']
    if f and f.id_delegacion:
        p.delegacion_activa = f.id_delegacion
        p.delegaciones_autorizadas.add(f.id_delegacion)
    p.estado = 'Activo'
    p.save()

    if f:
        Actividad.objects.filter(id_funcionario=f).update(usuario_creador=u)
        Compromiso.objects.filter(id_responsable=f).update(usuario_creador=u)

    print(f'[OK] Cuenta lista: {u.username} | {u.email} -> Funcionario: {f.nombre if f else "None"}')

print('\n=== RESUMEN FINAL DE CUENTAS ===')
for u in User.objects.all().order_by('id'):
    f = getattr(u, 'funcionario', None)
    if not f:
        f = Funcionario.objects.filter(user=u).first()
    p = getattr(u, 'perfil', None)
    grp = list(u.groups.values_list('name', flat=True))
    rol_cod = p.rol.codigo if p and p.rol else 'N/A'
    del_nom = p.delegacion_activa.nombre if p and p.delegacion_activa else 'N/A'
    print(f'User: {u.username:<15} | Email: {u.email:<25} | Grupo: {grp} | Rol: {rol_cod} | Del: {del_nom} | Func: {f.nombre if f else "None"}')
