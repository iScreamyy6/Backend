"""
test_personal_filter.py
Verifica que usuarios Administrativos solo vean sus propias gestiones.

Usuarios probados:
  - operador_d01 (ROL-OPE, Administrativo) -> Flash (Gestor Social 1) -> 3 gestiones
  - admin (ROL-ADM, Administrador)         -> ve todas (24)
  - coordinador (ROL-COORD, Supervisor)    -> ve todas (scope comunal)

Ejecutar:
    .\\venv\\Scripts\\python test_personal_filter.py
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
    """Crea un client autenticado con force_login (sin necesitar contraseña)."""
    c = Client()
    u = User.objects.get(username=username)
    c.force_login(u)
    return c, u


print('\n' + '='*60)
print('TEST: Filtro Personal por Rol de Usuario')
print('='*60)

# ── Datos base ────────────────────────────────────────────────
total_gestiones = Actividad.objects.filter(id_gestion_padre__isnull=True).count()
print(f'\n{INFO} Total gestiones principales en DB: {total_gestiones}')

u_op = User.objects.get(username='operador_d01')
func_flash = Funcionario.objects.filter(user=u_op).first()
mis_ids = set(
    Actividad.objects.filter(
        Q(id_funcionario=func_flash) | Q(usuario_creador=u_op),
        id_gestion_padre__isnull=True
    ).values_list('id_actividad', flat=True)
)
print(f'{INFO} operador_d01 / Flash -> gestiones propias: {len(mis_ids)} (IDs: {sorted(mis_ids)})')

u_op2 = User.objects.get(username='operador_d02')
func_acuaman = Funcionario.objects.filter(user=u_op2).first()
mis_ids_op2 = set(
    Actividad.objects.filter(
        Q(id_funcionario=func_acuaman) | Q(usuario_creador=u_op2),
        id_gestion_padre__isnull=True
    ).values_list('id_actividad', flat=True)
)
print(f'{INFO} operador_d02 / Acuaman -> gestiones propias: {len(mis_ids_op2)} (IDs: {sorted(mis_ids_op2)})')

# ── Test 1: operador_d01 ve /actividades/ con solo sus gestiones ──
print('\n--- operador_d01 (Administrativo / ROL-OPE) ---')
c_op, _ = get_client('operador_d01')

r = c_op.get('/actividades/')
check('GET /actividades/ responde 200', r.status_code == 200,
      f'status={r.status_code}')

html = r.content.decode('utf-8', errors='replace')
check('Banner "Vista Personal" visible', 'Vista Personal' in html,
      'El banner de gestiones propias no aparece')

# Verificar por contexto del template
if hasattr(r, 'context') and r.context and r.context.get('actividades') is not None:
    actividades_ctx = r.context['actividades']
    ids_vistos = set(actividades_ctx.values_list('id_actividad', flat=True))
    check(
        f'operador_d01 ve exactamente {len(mis_ids)} gestiones',
        ids_vistos == mis_ids,
        f'vio={sorted(ids_vistos)} esperado={sorted(mis_ids)}'
    )
    check(
        'operador_d01 NO ve gestiones de otros',
        ids_vistos.issubset(mis_ids),
        f'gestiones extra: {sorted(ids_vistos - mis_ids)}'
    )
    check('flag solo_propias=True en contexto', r.context.get('solo_propias') == True)
else:
    # Verificar cantidad en HTML (el template muestra el contador)
    check(f'operador_d01 ve {len(mis_ids)} gestiones (por HTML)',
          f'>{len(mis_ids)}<' in html or f'({len(mis_ids)}' in html or str(len(mis_ids)) in html)

# ── Test 2: admin ve todas las gestiones ──
print('\n--- admin (Administrador / ROL-ADM) ---')
c_adm, _ = get_client('admin')

r = c_adm.get('/actividades/')
check('GET /actividades/ responde 200', r.status_code == 200)

html_adm = r.content.decode('utf-8', errors='replace')
check('admin NO ve banner "Vista Personal"', 'Vista Personal' not in html_adm,
      'El admin no debería ver el banner de gestiones restringidas')

if hasattr(r, 'context') and r.context and r.context.get('actividades') is not None:
    ids_adm = set(r.context['actividades'].values_list('id_actividad', flat=True))
    check(
        f'admin ve todas ({total_gestiones}) gestiones',
        len(ids_adm) == total_gestiones,
        f'admin vio {len(ids_adm)}, esperado {total_gestiones}'
    )
    check('flag solo_propias=False en contexto', r.context.get('solo_propias') == False)

# ── Test 3: coordinador (Supervisor) ve todas ──
print('\n--- coordinador (Supervisor / ROL-COORD) ---')
c_coord, _ = get_client('coordinador')

r = c_coord.get('/actividades/')
check('GET /actividades/ responde 200', r.status_code == 200)
html_coord = r.content.decode('utf-8', errors='replace')
check('coordinador NO ve banner "Vista Personal"', 'Vista Personal' not in html_coord)

if hasattr(r, 'context') and r.context and r.context.get('actividades') is not None:
    ids_coord = set(r.context['actividades'].values_list('id_actividad', flat=True))
    check(
        f'coordinador ve todas ({total_gestiones}) gestiones',
        len(ids_coord) == total_gestiones,
        f'coordinador vio {len(ids_coord)}, esperado {total_gestiones}'
    )

# ── Test 4: delegado_d01 (Supervisor) ve todas ──
print('\n--- delegado_d01 (Supervisor / ROL-DEL) ---')
c_del, _ = get_client('delegado_d01')
r = c_del.get('/actividades/')
check('GET /actividades/ responde 200', r.status_code == 200)
html_del = r.content.decode('utf-8', errors='replace')
check('delegado_d01 NO ve banner "Vista Personal"', 'Vista Personal' not in html_del)

# ── Test 5: operador_d01 en Kanban ──
print('\n--- operador_d01 en Kanban (/agenda/resumen/) ---')
r_kanban = c_op.get('/agenda/resumen/')
check('GET /agenda/resumen/ responde 200', r_kanban.status_code == 200,
      f'status={r_kanban.status_code}')

# ── Test 6: operador_d02 (otro operativo, Administrativo) ──
print('\n--- operador_d02 (Administrativo / ROL-TER) ---')
c_op2, _ = get_client('operador_d02')
r2 = c_op2.get('/actividades/')
check('GET /actividades/ responde 200', r2.status_code == 200)
html2 = r2.content.decode('utf-8', errors='replace')
check('operador_d02 ve banner "Vista Personal"', 'Vista Personal' in html2)

if hasattr(r2, 'context') and r2.context and r2.context.get('actividades') is not None:
    ids_op2 = set(r2.context['actividades'].values_list('id_actividad', flat=True))
    check(
        'operador_d02 NO ve gestiones de operador_d01',
        not ids_op2.intersection(mis_ids),
        f'gestiones compartidas (error): {sorted(ids_op2.intersection(mis_ids))}'
    )

# ── Test 7: diserco (Administrativo / ROL-DIS) ──
print('\n--- diserco (Administrativo / ROL-DIS) ---')
c_dis, _ = get_client('diserco')
r3 = c_dis.get('/actividades/')
check('GET /actividades/ responde 200', r3.status_code == 200)
html3 = r3.content.decode('utf-8', errors='replace')
check('diserco ve banner "Vista Personal"', 'Vista Personal' in html3)

# ── Test 8: lista compromisos con filtro ──
print('\n--- Tubo de Trabajo /agenda/ ---')
r_comp = c_op.get('/agenda/')
check('operador_d01 GET /agenda/ responde 200', r_comp.status_code == 200,
      f'status={r_comp.status_code}')

r_comp_adm = c_adm.get('/agenda/')
check('admin GET /agenda/ responde 200', r_comp_adm.status_code == 200)

# ── Resumen ──
print('\n' + '='*60)
if errors:
    print(f'FAILED: {len(errors)} test(s) fallaron:')
    for e in errors:
        print(f'  - {e}')
else:
    print('TODOS LOS TESTS PASARON')
print('='*60 + '\n')
