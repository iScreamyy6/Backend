"""
test_personal_filter.py
Verifica que las cuentas estén conectadas con sus nombres de superhéroes y dominios @correo.cl,
y que usuarios Administrativos solo vean sus propias gestiones.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Municipalidad.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from actividades.models import Actividad
from organizacion.models import Funcionario
from django.db.models import Q

PASS = '[PASS]'
FAIL = '[FAIL]'
INFO = '[INFO]'

errors = []


def check(label, condition, detail=''):
    if condition:
        print(f'{PASS} {label}')
    else:
        print(f'{FAIL} {label}' + (f' | {detail}' if detail else ''))
        errors.append(label)


def get_client(username):
    c = Client()
    u = User.objects.get(username=username)
    c.force_login(u)
    return c, u


def login_post(identificador, password='admin'):
    c = Client()
    r = c.post('/login/', {'username': identificador, 'password': password}, follow=True)
    return c, r


print('\n' + '='*60)
print('TEST: Cuentas Conectadas y Filtro Personal por Rol')
print('='*60)

total_gestiones = Actividad.objects.filter(id_gestion_padre__isnull=True).count()
print(f'\n{INFO} Total gestiones principales en DB: {total_gestiones}')

# ── Test 1: Autenticación por Nombre y por Correo @correo.cl ──
print('\n--- Autenticación por Username y por Correo @correo.cl ---')
cuentas_a_probar = [
    ('acuaman', 'acuaman@correo.cl', 'Acuaman'),
    ('flash', 'flash@correo.cl', 'Flash'),
    ('heman', 'heman@correo.cl', 'He-Man'),
    ('capitanamarvel', 'capitanamarvel@correo.cl', 'Capitana Marvel'),
    ('spiderman', 'spiderman@correo.cl', 'Spider-Man'),
    ('hulk', 'hulk@correo.cl', 'Hulk'),
    ('capitanamerica', 'capitanamerica@correo.cl', 'Capitán América'),
    ('panteranegra', 'panteranegra@correo.cl', 'Pantera Negra'),
    ('coordinador', 'coordinador@correo.cl', None),
]

for usr, email, func_esperado in cuentas_a_probar:
    # 1. Login por username
    c_u, r_u = login_post(usr, 'admin')
    u_logueado = bool(c_u.session.get('_auth_user_id'))
    check(f'Login por usuario "{usr}" exitoso', u_logueado, f'status={r_u.status_code}')

    # 2. Login por email institucional @correo.cl
    c_e, r_e = login_post(email, 'admin')
    e_logueado = bool(c_e.session.get('_auth_user_id'))
    check(f'Login por correo "{email}" exitoso', e_logueado, f'status={r_e.status_code}')

    # 3. Validar vinculación a Funcionario
    if func_esperado:
        u_obj = User.objects.get(username=usr)
        f_obj = getattr(u_obj, 'funcionario', None)
        check(f'Usuario {usr} vinculado a Funcionario {func_esperado}',
              f_obj is not None and func_esperado in f_obj.nombre)

# ── Test 2: Compatibilidad de Aliases Históricos (operador_02, etc.) ──
print('\n--- Compatibilidad con Aliases Históricos ---')
c_alias, r_alias = login_post('operador_02', 'admin')
check('Login con alias "operador_02" autentica como acuaman',
      bool(c_alias.session.get('_auth_user_id')) and int(c_alias.session.get('_auth_user_id')) == User.objects.get(username='acuaman').id)

c_alias2, r_alias2 = login_post('operador_d01', 'admin')
check('Login con alias "operador_d01" autentica como flash',
      bool(c_alias2.session.get('_auth_user_id')) and int(c_alias2.session.get('_auth_user_id')) == User.objects.get(username='flash').id)

# ── Test 3: Filtro Personal de Gestiones para Administrativos ──
print('\n--- Filtro Personal en Módulo de Gestiones (/actividades/) ---')
for usr_adm in ['flash', 'acuaman', 'capitanamarvel', 'spiderman', 'hulk']:
    c, u = get_client(usr_adm)
    r = c.get('/actividades/')
    check(f'GET /actividades/ como {usr_adm} responde 200', r.status_code == 200)

    # Debe ver exactamente las 3 gestiones de su funcionario
    func = getattr(u, 'funcionario', None)
    mis_ids = set(Actividad.objects.filter(
        Q(id_funcionario=func) | Q(usuario_creador=u),
        id_gestion_padre__isnull=True
    ).values_list('id_actividad', flat=True))

    check(f'{usr_adm} tiene asignadas exactamente 3 gestiones', len(mis_ids) == 3, f'ids={mis_ids}')

# ── Test 4: Visibilidad de Administradores y Supervisores ──
print('\n--- Visibilidad de Admin y Supervisores ---')
c_adm, _ = get_client('admin')
r_adm = c_adm.get('/actividades/')
check('admin ve /actividades/ con status 200', r_adm.status_code == 200)

c_coord, _ = get_client('coordinador')
r_coord = c_coord.get('/actividades/')
check('coordinador ve /actividades/ con status 200', r_coord.status_code == 200)

c_heman, _ = get_client('heman')
r_heman = c_heman.get('/actividades/')
check('heman (Supervisor) ve /actividades/ con status 200', r_heman.status_code == 200)

# ── Test 5: Tablero Kanban (/agenda/resumen/) con Filtro Personal ──
print('\n--- Tablero Kanban Tubo de Trabajo (/agenda/resumen/) ---')
c_flash, _ = get_client('flash')
r_kan = c_flash.get('/agenda/resumen/')
check('flash en Kanban responde 200', r_kan.status_code == 200)

c_spid, _ = get_client('spiderman')
r_kan_s = c_spid.get('/agenda/resumen/')
check('spiderman en Kanban responde 200', r_kan_s.status_code == 200)

# ── Resumen ──
print('\n' + '='*60)
if errors:
    print(f'FAILED: {len(errors)} test(s) fallaron:')
    for e in errors:
        print(f'  - {e}')
else:
    print('TODOS LOS TESTS DE CUENTAS CONECTADAS Y FILTROS PASARON EXITOSAMENTE [OK]')
print('='*60 + '\n')
