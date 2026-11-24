"""
Script de repoblamiento institucional limpio para demostraciones.
Elimina registros transaccionales previos y crea datos representativos
para todas las funciones del proyecto SGR:
- 10 Vecinos
- 8 Territorios (2 por delegacion)
- 8 Juntas de Vecinos con sus Directivas
- 16 Metas de Funcionarios (4 funcionarios al 100% en Q4 2026)
- 24 Gestiones Unificadas (Sociales, Terreno, Tubo)
- 13 Compromisos en Tubo de Trabajo (Kanban equilibrado con atrasadas)
- 4 Atenciones Ciudadanas
- 2 Fichas de Gestor Social
- 4 Indicadores de Delegacion (Q4 2026)
"""
import os
import django
from datetime import date, timedelta
from decimal import Decimal
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Municipalidad.settings')
django.setup()

from django.contrib.auth.models import User, Group
from organizacion.models import (
    Delegacion, Territorio, JuntaVecinos, ParticipacionJunta,
    Funcionario, PerfilUsuario, Rol
)
from actividades.models import (
    Vecino, Actividad, AtencionCiudadana, GestionSocial,
    TipoAtencion, SubAtencion
)
from agenda.models import Compromiso
from resultados.models import (
    PeriodoEvaluacion, MetaFuncionario, IndicadorDelegacion, ItemMeta
)

print("--- INICIANDO LIMPIEZA DE REGISTROS TRANSACCIONALES ---")

# 1. Eliminacion en cascada limpia de registros previos
Actividad.objects.all().delete()
Compromiso.objects.all().delete()
AtencionCiudadana.objects.all().delete()
GestionSocial.objects.all().delete()
MetaFuncionario.objects.all().delete()
IndicadorDelegacion.objects.all().delete()
ParticipacionJunta.objects.all().delete()
JuntaVecinos.objects.all().delete()
Territorio.objects.all().delete()
Vecino.objects.all().delete()
PeriodoEvaluacion.objects.filter(nombre__icontains='Suite Test').delete()
PeriodoEvaluacion.objects.filter(nombre__icontains='Trimestre Suite').delete()
User.objects.filter(username__in=['nuevo_supervisor_test', 'test_user_suite']).delete()
Rol.objects.filter(nombre__icontains='Test Auto').delete()

print("[OK] Registros transaccionales anteriores eliminados correctamente.")

# 2. Asegurar Períodos Evaluativos
p4, _ = PeriodoEvaluacion.objects.get_or_create(
    nombre='4to Trimestre 2026',
    defaults={
        'fecha_inicio': date(2026, 10, 1),
        'fecha_cierre': date(2026, 12, 31),
        'dias_totales': 92,
        'dias_transcurridos': 48,
        'activo': True
    }
)
p4.fecha_inicio = date(2026, 10, 1)
p4.fecha_cierre = date(2026, 12, 31)
p4.dias_totales = 92
p4.dias_transcurridos = 48
p4.activo = True
p4.save()

p3, _ = PeriodoEvaluacion.objects.get_or_create(
    nombre='3er Trimestre 2026 (Cerrado)',
    defaults={
        'fecha_inicio': date(2026, 7, 1),
        'fecha_cierre': date(2026, 9, 30),
        'dias_totales': 92,
        'dias_transcurridos': 92,
        'activo': False
    }
)
p3.activo = False
p3.save()

p2, _ = PeriodoEvaluacion.objects.get_or_create(
    nombre='2do Trimestre 2026 (Cerrado)',
    defaults={
        'fecha_inicio': date(2026, 4, 1),
        'fecha_cierre': date(2026, 6, 30),
        'dias_totales': 91,
        'dias_transcurridos': 91,
        'activo': False
    }
)
p2.activo = False
p2.save()

# Delegaciones
d_comp = Delegacion.objects.filter(nombre__icontains='Compañías').first() or Delegacion.objects.get(pk=1)
d_antena = Delegacion.objects.filter(nombre__icontains='Antena').first() or Delegacion.objects.get(pk=2)
d_centro = Delegacion.objects.filter(nombre__icontains='Centro').first() or Delegacion.objects.get(pk=3)
d_rural = Delegacion.objects.filter(nombre__icontains='Rural').first() or Delegacion.objects.get(pk=4)

# 3. Creacion de Vecinos (10 representativos con datos reales de La Serena)
vecinos_datos = [
    {
        'rut': '14.521.890-3',
        'nombre': 'Gonzalo Andrés Pizarro',
        'telefono': '+56 9 8452 1109',
        'correo': 'gonzalo.pizarro@correo.cl',
        'direccion': 'Calle 18 de Septiembre #450, La Antena',
        'territorio': 'Sector La Antena y Santa Inés'
    },
    {
        'rut': '13.904.551-8',
        'nombre': 'Lorena Patricia Carmona Díaz',
        'telefono': '+56 9 7611 2345',
        'correo': 'lorena.carmona@correo.cl',
        'direccion': 'Pasaje Los Conquistadores #124, La Florida',
        'territorio': 'Sector La Florida y Pan de Azúcar'
    },
    {
        'rut': '15.312.890-4',
        'nombre': 'Hernán Rodrigo Pizarro Vega',
        'telefono': '+56 9 9123 4567',
        'correo': 'hernan.pizarro@correo.cl',
        'direccion': 'Av. Alberto Arenas #2210, El Milagro',
        'territorio': 'Sector San Joaquín y El Milagro'
    },
    {
        'rut': '16.543.210-9',
        'nombre': 'Juana de Lourdes Rojas Pérez',
        'telefono': '+56 9 7123 4590',
        'correo': 'juana.rojas@correo.cl',
        'direccion': 'Calle Esmeralda #210, Las Compañías',
        'territorio': 'Sector Las Compañías Bajas'
    },
    {
        'rut': '14.238.901-2',
        'nombre': 'María Elena González Silva',
        'telefono': '+56 9 8543 2199',
        'correo': 'maria.gonzalez@correo.cl',
        'direccion': 'Pasaje Las Minas #88, Las Compañías',
        'territorio': 'Sector El Brillador y Viña del Mar'
    },
    {
        'rut': '18.234.567-1',
        'nombre': 'Esteban Andrés Munizaga Morales',
        'telefono': '+56 9 6543 2198',
        'correo': 'esteban.munizaga@correo.cl',
        'direccion': 'Calle Principal s/n, Las Rojas',
        'territorio': 'Sector Altovalsol y Las Rojas'
    },
    {
        'rut': '12.789.456-2',
        'nombre': 'Marcela Patricia Núñez',
        'telefono': '+56 9 7890 1234',
        'correo': 'marcela.nunez@correo.cl',
        'direccion': 'Calle Balmaceda #1458, La Serena',
        'territorio': 'Sector Balmaceda y La Pampa'
    },
    {
        'rut': '11.876.543-9',
        'nombre': 'Valeria Soledad Pinto',
        'telefono': '+56 9 8901 2345',
        'correo': 'valeria.pinto@correo.cl',
        'direccion': 'Calle Los Carrera #340, Centro',
        'territorio': 'Sector Casco Histórico y Colina El Pino'
    },
    {
        'rut': '15.432.109-8',
        'nombre': 'Fernando Javier Godoy',
        'telefono': '+56 9 9012 3456',
        'correo': 'fernando.godoy@correo.cl',
        'direccion': 'Camino Vecinal El Romero Lote 4',
        'territorio': 'Sector Rural El Romero'
    },
    {
        'rut': '13.210.987-7',
        'nombre': 'Carmen Gloria Valenzuela',
        'telefono': '+56 9 6789 0123',
        'correo': 'carmen.valenzuela@correo.cl',
        'direccion': 'Pasaje El Brillador #50, Las Compañías',
        'territorio': 'Sector El Brillador y Viña del Mar'
    },
]

vecinos_dict = {}
for vd in vecinos_datos:
    v = Vecino.objects.create(
        rut=vd['rut'],
        nombre=vd['nombre'],
        telefono=vd['telefono'],
        correo=vd['correo'],
        direccion=vd['direccion'],
        territorio=vd['territorio']
    )
    vecinos_dict[v.rut] = v

print(f"[OK] {len(vecinos_dict)} Vecinos creados.")

# 4. Creacion de Territorios (8 territorios: 2 por delegacion)
territorios_datos = [
    # D01 - Las Compañías
    {'nombre': 'Sector Las Compañías Bajas', 'delegacion': d_comp, 'descripcion': 'Sector poniente y fundacional de Las Compañías, colindante con Ruta 5 y borde río.'},
    {'nombre': 'Sector El Brillador y Viña del Mar', 'delegacion': d_comp, 'descripcion': 'Eje norte de Las Compañías, Villa Lambert, El Brillador y Villa Viña del Mar.'},
    # D02 - La Antena
    {'nombre': 'Sector La Antena y Santa Inés', 'delegacion': d_antena, 'descripcion': 'Sector histórico de La Antena, colindante con Santa Inés y subida 18 de Septiembre.'},
    {'nombre': 'Sector La Florida y Pan de Azúcar', 'delegacion': d_antena, 'descripcion': 'Cuadrante residencial de La Florida alta, Villa El Indio y accesos a Ruta D-41.'},
    # D03 - Centro
    {'nombre': 'Sector Casco Histórico y Colina El Pino', 'delegacion': d_centro, 'descripcion': 'Zona patrimonial, perímetro centro, campus universitario y faldeos poniente Cerro Grande.'},
    {'nombre': 'Sector Balmaceda y La Pampa', 'delegacion': d_centro, 'descripcion': 'Eje comercial y residencial Av. Balmaceda, Cuatro Esquinas y sector La Pampa.'},
    # D04 - Rural
    {'nombre': 'Sector Altovalsol y Las Rojas', 'delegacion': d_rural, 'descripcion': 'Cuenca media del Río Elqui, pueblos rurales de Altovalsol, Las Rojas y Quebrada de Talca.'},
    {'nombre': 'Sector Rural El Romero', 'delegacion': d_rural, 'descripcion': 'Franja agrícola norte del valle, comunidades de El Romero, Coquimbito y La Estrella.'},
]

territorios_dict = {}
for td in territorios_datos:
    t = Territorio.objects.create(
        nombre=td['nombre'],
        delegacion=td['delegacion'],
        descripcion=td['descripcion'],
        estado='Activo'
    )
    territorios_dict[t.nombre] = t

print(f"[OK] {len(territorios_dict)} Territorios creados.")

# 5. Creacion de Juntas de Vecinos (8 JJVV)
juntas_datos = [
    {'nombre': "Junta de Vecinos Bernardo O'Higgins de La Antena", 'delegacion': d_antena, 'territorio': territorios_dict['Sector La Antena y Santa Inés'], 'dir': 'Calle 18 de Septiembre #450', 'f': date(1988, 5, 12)},
    {'nombre': 'Junta de Vecinos Villa El Indio', 'delegacion': d_antena, 'territorio': territorios_dict['Sector La Florida y Pan de Azúcar'], 'dir': 'Pasaje Los Conquistadores #120', 'f': date(1994, 8, 24)},
    {'nombre': 'Junta de Vecinos Villa San Bartolomé', 'delegacion': d_comp, 'territorio': territorios_dict['Sector Las Compañías Bajas'], 'dir': 'Calle Esmeralda #340', 'f': date(1996, 6, 10)},
    {'nombre': 'Junta de Vecinos El Brillador Alto', 'delegacion': d_comp, 'territorio': territorios_dict['Sector El Brillador y Viña del Mar'], 'dir': 'Pasaje La Mina #88', 'f': date(2001, 9, 8)},
    {'nombre': 'Unión Vecinal Casco Histórico', 'delegacion': d_centro, 'territorio': territorios_dict['Sector Casco Histórico y Colina El Pino'], 'dir': 'Calle Los Carrera #340', 'f': date(1992, 3, 15)},
    {'nombre': 'Junta de Vecinos Alborada - Balmaceda', 'delegacion': d_centro, 'territorio': territorios_dict['Sector Balmaceda y La Pampa'], 'dir': 'Calle Balmaceda #1450', 'f': date(1991, 4, 3)},
    {'nombre': 'Junta de Vecinos Las Rojas Centro', 'delegacion': d_rural, 'territorio': territorios_dict['Sector Altovalsol y Las Rojas'], 'dir': 'Calle Principal s/n', 'f': date(1985, 3, 14)},
    {'nombre': 'Comité Vecinal El Romero', 'delegacion': d_rural, 'territorio': territorios_dict['Sector Rural El Romero'], 'dir': 'Camino Vecinal El Romero Lote 4', 'f': date(1998, 7, 29)},
]

juntas_dict = {}
for jd in juntas_datos:
    j = JuntaVecinos.objects.create(
        nombre=jd['nombre'],
        delegacion=jd['delegacion'],
        territorio=jd['territorio'],
        direccion=jd['dir'],
        fecha_constitucion=jd['f'],
        estado='Activa'
    )
    juntas_dict[j.nombre] = j

print(f"[OK] {len(juntas_dict)} Juntas de Vecinos creadas.")

# 6. Directivas de Juntas de Vecinos (8 dirigentes)
directivas = [
    {'junta': juntas_dict["Junta de Vecinos Bernardo O'Higgins de La Antena"], 'vecino': vecinos_dict['14.521.890-3'], 'cargo': 'Presidente/a'},
    {'junta': juntas_dict['Junta de Vecinos Villa El Indio'], 'vecino': vecinos_dict['13.904.551-8'], 'cargo': 'Presidente/a'},
    {'junta': juntas_dict['Junta de Vecinos Villa San Bartolomé'], 'vecino': vecinos_dict['16.543.210-9'], 'cargo': 'Presidente/a'},
    {'junta': juntas_dict['Junta de Vecinos El Brillador Alto'], 'vecino': vecinos_dict['14.238.901-2'], 'cargo': 'Presidente/a'},
    {'junta': juntas_dict['Unión Vecinal Casco Histórico'], 'vecino': vecinos_dict['11.876.543-9'], 'cargo': 'Presidente/a'},
    {'junta': juntas_dict['Junta de Vecinos Alborada - Balmaceda'], 'vecino': vecinos_dict['12.789.456-2'], 'cargo': 'Presidente/a'},
    {'junta': juntas_dict['Junta de Vecinos Las Rojas Centro'], 'vecino': vecinos_dict['18.234.567-1'], 'cargo': 'Presidente/a'},
    {'junta': juntas_dict['Comité Vecinal El Romero'], 'vecino': vecinos_dict['15.432.109-8'], 'cargo': 'Presidente/a'},
]

for d in directivas:
    ParticipacionJunta.objects.create(
        vecino=d['vecino'],
        junta=d['junta'],
        cargo=d['cargo'],
        es_dirigente=True,
        fecha_incorporacion=date(2024, 1, 15),
        estado='Activo'
    )

print(f"[OK] {len(directivas)} Directivas de JJVV asignadas.")

# 7. Obtener Funcionarios
f_acuaman = Funcionario.objects.filter(nombre__icontains='Acuaman').first()
f_flash = Funcionario.objects.filter(nombre__icontains='Flash').first()
f_hulk = Funcionario.objects.filter(nombre__icontains='Hulk').first()
f_heman = Funcionario.objects.filter(nombre__icontains='He-Man').first()
f_spiderman = Funcionario.objects.filter(nombre__icontains='Spider-Man').first()
f_capamerica = Funcionario.objects.filter(nombre__icontains='Capitán América').first()
f_capmarvel = Funcionario.objects.filter(nombre__icontains='Capitana Marvel').first()
f_pantera = Funcionario.objects.filter(nombre__icontains='Pantera Negra').first()

# 8. Asignacion de Metas a Funcionarios (16 metas en Q4 2026 - 80% ponderacion c/u, dejando 20% disponible para asignaciones)
metas_data = [
    # Acuaman (La Antena - D02) -> Total 80% (Disponible 20%)
    (f_acuaman, 'ATENCIÓN DE USUARIO PRESENCIAL Y TELEFÓNICA', Decimal('20.00'), 40),
    (f_acuaman, 'INFORMES SOCIALES Y FICHAS FIBE', Decimal('25.00'), 20),
    (f_acuaman, 'GESTIÓN TERRITORIAL Y OPERATIVOS', Decimal('20.00'), 15),
    (f_acuaman, 'EMERGENCIAS COMUNALES Y REUNIONES', Decimal('15.00'), 10),
    # Flash (Las Compañías - D01) -> Total 80% (Disponible 20%)
    (f_flash, 'ATENCIÓN SOCIAL Y RECEPCIÓN DE SOLICITUDES', Decimal('25.00'), 45),
    (f_flash, 'VISITAS DOMICILIARIAS Y FICHA FIBE', Decimal('25.00'), 30),
    (f_flash, 'GESTIÓN DE AYUDAS SOCIALES PALIATIVAS', Decimal('15.00'), 25),
    (f_flash, 'SEGUIMIENTO CASOS DE ALTA COMPLEJIDAD', Decimal('15.00'), 10),
    # Hulk (Centro - D03) -> Total 80% (Disponible 20%)
    (f_hulk, 'ATENCIÓN SOCIAL A USUARIO PRESENCIAL', Decimal('25.00'), 50),
    (f_hulk, 'VISITA A TERRENO Y PERITAJE', Decimal('25.00'), 30),
    (f_hulk, 'ENTREGA DE INFORME Y BENEFICIO', Decimal('20.00'), 25),
    (f_hulk, 'EMERGENCIA SOCIAL INMEDIATA', Decimal('10.00'), 15),
    # He-Man (Las Compañías - D01) -> Total 80% (Disponible 20%)
    (f_heman, 'COORDINACIÓN DE OPERATIVOS TERRITORIALES', Decimal('25.00'), 30),
    (f_heman, 'SUPERVISIÓN Y CONTROL DE COMPROMISOS', Decimal('25.00'), 25),
    (f_heman, 'MESAS BARRIALES Y REUNIONES CON JJVV', Decimal('15.00'), 15),
    (f_heman, 'GESTIÓN DE EMERGENCIAS COMUNALES', Decimal('15.00'), 10),
]

for func, item, pond, meta in metas_data:
    if func:
        MetaFuncionario.objects.create(
            id_funcionario=func,
            id_periodo=p4,
            item=item,
            ponderador=pond,
            meta_periodo=meta,
            avance_actual=0,
            usuario_registro=func.user
        )

print(f"[OK] {len(metas_data)} Metas de Funcionarios asignadas al 4to Trimestre 2026.")

# 9. Obtener Tipo y SubAtencion para gestiones
tipo_soc = TipoAtencion.objects.filter(nombre__icontains='Social').first() or TipoAtencion.objects.first()
sub_soc = SubAtencion.objects.filter(id_tipo=tipo_soc).first() or SubAtencion.objects.first()

tipo_ter = TipoAtencion.objects.filter(nombre__icontains='Territorial').first() or tipo_soc
sub_ter = SubAtencion.objects.filter(id_tipo=tipo_ter).first() or sub_soc

# 10. Creacion de EXACTAMENTE 13 Compromisos en Tubo de Trabajo
# 3 PENDIENTES, 5 EN PROCESO, 3 REALIZADOS, 2 ATRASADOS (fecha compromiso vencida respecto a hoy 17-Nov-2026)
compromisos_datos = [
    # EN PROCESO (5)
    {
        'fecha_solicitud': date(2026, 11, 2),
        'fecha_compromiso': date(2026, 11, 9),
        'tipo': 'INT',
        'actividad': 'Coordinación de operativo municipal integral en Las Compañías Bajas',
        'solicitante': 'Carmen Gloria Valenzuela',
        'territorio': 'Sector Las Compañías Bajas',
        'responsable': f_heman.nombre if f_heman else 'He-Man',
        'id_responsable': f_heman,
        'id_delegacion': d_comp,
        'area_apoyo': 'Delegación Las Compañías',
        'estado': 'EN PROCESO',
        'observaciones': 'Coordinado con cuadrilla territorial para el viernes.'
    },
    {
        'fecha_solicitud': date(2026, 11, 2),
        'fecha_compromiso': date(2026, 11, 10),
        'tipo': 'EXT',
        'actividad': 'Nivelación de calzada y bacheo preventivo en Pasaje Los Conquistadores',
        'solicitante': 'Héctor Villalobos Tapia',
        'territorio': 'Sector La Florida y Pan de Azúcar',
        'responsable': f_spiderman.nombre if f_spiderman else 'Spider-Man',
        'id_responsable': f_spiderman,
        'id_delegacion': d_antena,
        'area_apoyo': 'Operaciones y Vialidad',
        'estado': 'EN PROCESO',
        'observaciones': 'Maquinaria pesada programada para perfilado.'
    },
    {
        'fecha_solicitud': date(2026, 11, 2),
        'fecha_compromiso': date(2026, 11, 7),
        'tipo': 'EXT',
        'actividad': 'Operativo de desmalezado y perfilado de aceras en Villa Lambert',
        'solicitante': 'Marcela Patricia Núñez',
        'territorio': 'Sector El Brillador y Viña del Mar',
        'responsable': f_acuaman.nombre if f_acuaman else 'Acuaman',
        'id_responsable': f_acuaman,
        'id_delegacion': d_antena,
        'area_apoyo': 'Operaciones',
        'estado': 'EN PROCESO',
        'observaciones': 'Cuadrilla municipal ejecutó corte de maleza y retiro.'
    },
    {
        'fecha_solicitud': date(2026, 11, 2),
        'fecha_compromiso': date(2026, 11, 9),
        'tipo': 'INT',
        'actividad': 'Gestión de beneficio catastrófico y postulación habitacional',
        'solicitante': 'Fernando Javier Godoy',
        'territorio': 'Sector Rural El Romero',
        'responsable': f_capamerica.nombre if f_capamerica else 'Capitán América',
        'id_responsable': f_capamerica,
        'id_delegacion': d_rural,
        'area_apoyo': 'DIDECO / Asistencia Social',
        'estado': 'EN PROCESO',
        'observaciones': 'Ficha de protección y antecedentes en trámite.'
    },
    {
        'fecha_solicitud': date(2026, 11, 1),
        'fecha_compromiso': date(2026, 11, 8),
        'tipo': 'EXT',
        'actividad': 'Tramitación de subsidio de agua potable y canasta familiar',
        'solicitante': 'Mario Alberto Cortés',
        'territorio': 'Sector Las Compañías Bajas',
        'responsable': f_flash.nombre if f_flash else 'Flash',
        'id_responsable': f_flash,
        'id_delegacion': d_comp,
        'area_apoyo': 'DIDECO / Asistencia Social',
        'estado': 'EN PROCESO',
        'observaciones': 'Documentación social y Registro Social de Hogares en verificación.'
    },
    # PENDIENTES / ATRASADOS (3)
    {
        'fecha_solicitud': date(2026, 11, 1),
        'fecha_compromiso': date(2026, 11, 11),
        'tipo': 'EXT',
        'actividad': 'Levantamiento planimétrico de accesibilidad peatonal en Centro',
        'solicitante': 'Francisca Belén Santander',
        'territorio': 'Sector Casco Histórico y Colina El Pino',
        'responsable': f_pantera.nombre if f_pantera else 'Pantera Negra',
        'id_responsable': f_pantera,
        'id_delegacion': d_centro,
        'area_apoyo': 'Planificación y Obras',
        'estado': 'EN PROCESO',
        'observaciones': 'Levantamiento topográfico en terreno.'
    },
    {
        'fecha_solicitud': date(2026, 11, 1),
        'fecha_compromiso': date(2026, 11, 9),
        'tipo': 'EXT',
        'actividad': 'Poda preventiva y despeje de ramas sobre tendido eléctrico',
        'solicitante': 'Silvia Inés Pastén',
        'territorio': 'Sector Altovalsol y Las Rojas',
        'responsable': f_capmarvel.nombre if f_capmarvel else 'Capitana Marvel',
        'id_responsable': f_capmarvel,
        'id_delegacion': d_rural,
        'area_apoyo': 'Aseo y Ornato / DISERCO',
        'estado': 'EN PROCESO',
        'observaciones': 'Permisos de CGE gestionados para corte programado.'
    },
    # REALIZADOS (3)
    {
        'fecha_solicitud': date(2026, 10, 30),
        'fecha_compromiso': date(2026, 11, 3),
        'tipo': 'EXT',
        'actividad': 'Operativo de retiro de voluminosos y limpieza en Quebrada',
        'solicitante': 'Oscar Armando Galleguillos',
        'territorio': 'Sector Rural El Romero',
        'responsable': f_capmarvel.nombre if f_capmarvel else 'Capitana Marvel',
        'id_responsable': f_capmarvel,
        'id_delegacion': d_rural,
        'area_apoyo': 'Aseo y Ornato / DISERCO',
        'estado': 'REALIZADO',
        'observaciones': 'Retiro de 8 toneladas de escombros y ramas.'
    },
    {
        'fecha_solicitud': date(2026, 10, 29),
        'fecha_compromiso': date(2026, 11, 2),
        'tipo': 'INT',
        'actividad': 'Mantención y mejoramiento de luminarias LED en Calle 18 de Septiembre',
        'solicitante': 'Andrés Sebastián Barraza',
        'territorio': 'Sector La Antena y Santa Inés',
        'responsable': f_acuaman.nombre if f_acuaman else 'Acuaman',
        'id_responsable': f_acuaman,
        'id_delegacion': d_antena,
        'area_apoyo': 'Alumbrado Público',
        'estado': 'REALIZADO',
        'observaciones': 'Trabajos concluidos con reposición de luminarias viales.'
    },
    {
        'fecha_solicitud': date(2026, 10, 28),
        'fecha_compromiso': date(2026, 11, 3),
        'tipo': 'EXT',
        'actividad': 'Reparación y reposición de luminarias LED viales en Las Compañías',
        'solicitante': 'Juan Carlos Carvajal',
        'territorio': 'Sector Las Compañías Bajas',
        'responsable': f_spiderman.nombre if f_spiderman else 'Spider-Man',
        'id_responsable': f_spiderman,
        'id_delegacion': d_comp,
        'area_apoyo': 'Alumbrado Público',
        'estado': 'REALIZADO',
        'observaciones': 'Circuito de iluminación normalizado.'
    },
    # PENDIENTES CON FECHA VENCIDA (ATRASADAS PARA KANBAN) (3)
    {
        'fecha_solicitud': date(2026, 10, 28),
        'fecha_compromiso': date(2026, 11, 2), # Vencido respecto a 17-Nov-2026
        'tipo': 'EXT',
        'actividad': 'Visita de verificación social por vulnerabilidad de adulto mayor',
        'solicitante': 'Raúl Hernán Castillo',
        'territorio': 'Sector Casco Histórico y Colina El Pino',
        'responsable': f_hulk.nombre if f_hulk else 'Hulk',
        'id_responsable': f_hulk,
        'id_delegacion': d_centro,
        'area_apoyo': 'DIDECO / Adulto Mayor',
        'estado': 'PENDIENTE',
        'observaciones': 'Caso derivado por junta de vecinos.'
    },
    {
        'fecha_solicitud': date(2026, 10, 27),
        'fecha_compromiso': date(2026, 11, 1), # Vencido respecto a 17-Nov-2026
        'tipo': 'INT',
        'actividad': 'Visita domiciliaria urgente por situación de postración',
        'solicitante': 'Teresa Silva Monardez',
        'territorio': 'Sector Las Compañías Bajas',
        'responsable': f_flash.nombre if f_flash else 'Flash',
        'id_responsable': f_flash,
        'id_delegacion': d_comp,
        'area_apoyo': 'DIDECO',
        'estado': 'PENDIENTE',
        'observaciones': 'Vecina no se encontraba en el domicilio en primera visita.'
    },
    {
        'fecha_solicitud': date(2026, 10, 26),
        'fecha_compromiso': date(2026, 10, 31), # Vencido respecto a 17-Nov-2026
        'tipo': 'EXT',
        'actividad': 'Retiro de escombros y ramas caídas en Plaza La Antena',
        'solicitante': 'Lorena Andrea Vega',
        'territorio': 'Sector La Antena y Santa Inés',
        'responsable': f_spiderman.nombre if f_spiderman else 'Spider-Man',
        'id_responsable': f_spiderman,
        'id_delegacion': d_antena,
        'area_apoyo': 'Aseo y Ornato',
        'estado': 'PENDIENTE',
        'observaciones': 'Pendiente disponibilidad de camión tolva.'
    },
]

compromisos_creados = []
for cd in compromisos_datos:
    comp = Compromiso.objects.create(
        fecha_solicitud=cd['fecha_solicitud'],
        fecha_compromiso=cd['fecha_compromiso'],
        tipo=cd['tipo'],
        actividad=cd['actividad'],
        solicitante=cd['solicitante'],
        territorio=cd['territorio'],
        responsable=cd['responsable'],
        id_responsable=cd['id_responsable'],
        id_delegacion=cd['id_delegacion'],
        area_apoyo=cd['area_apoyo'],
        estado=cd['estado'],
        observaciones=cd['observaciones'],
        usuario_creador=cd['id_responsable'].user if cd['id_responsable'] and cd['id_responsable'].user else None
    )
    compromisos_creados.append(comp)

print(f"[OK] {len(compromisos_creados)} Compromisos creados en Tubo de Trabajo (exactamente 13).")

# 11. Creacion de EXACTAMENTE 24 Gestiones Unificadas (Actividades)
# Las primeras 13 enlazadas a los compromisos creados (para el Kanban y trazabilidad)
gestiones_datos = [
    # 13 Gestiones enlazadas a los 13 compromisos
    {
        'fecha': date(2026, 11, 2),
        'responsable': f_heman.nombre if f_heman else 'He-Man',
        'id_funcionario': f_heman,
        'id_delegacion': d_comp,
        'solicitante': 'Carmen Gloria Valenzuela',
        'rut': '13.210.987-7',
        'territorio': 'Sector Las Compañías Bajas',
        'item': 'COORDINACIÓN DE OPERATIVOS TERRITORIALES',
        'solicitud': 'Coordinación de operativo municipal integral en Las Compañías Bajas',
        'accion': 'Reunión de coordinación técnica con dirigentes vecinales.',
        'estado': 'En Proceso',
        'es_social': False,
        'ingreso_tubo': True,
        'compromiso': compromisos_creados[0],
        'estado_evidencia': 'Aprobada',
        'tipo_impacto': 'Cuantitativa',
        'obs_revision': 'Operativo coordinado y validado en terreno conforme a planificación comunal.',
    },
    {
        'fecha': date(2026, 11, 2),
        'responsable': f_spiderman.nombre if f_spiderman else 'Spider-Man',
        'id_funcionario': f_spiderman,
        'id_delegacion': d_antena,
        'solicitante': 'Héctor Villalobos Tapia',
        'rut': '14.521.890-3',
        'territorio': 'Sector La Florida y Pan de Azúcar',
        'item': 'GESTIÓN TERRITORIAL Y OPERATIVOS',
        'solicitud': 'Nivelación de calzada y bacheo preventivo en Pasaje Los Conquistadores',
        'accion': 'Evaluación técnica en terreno y programación de asfalto en frío.',
        'estado': 'En Proceso',
        'es_social': False,
        'ingreso_tubo': True,
        'compromiso': compromisos_creados[1],
        'estado_evidencia': 'Aprobada',
        'tipo_impacto': 'Cuantitativa',
        'obs_revision': 'Fotografía de evaluación y comprobante técnico verificados.',
    },
    {
        'fecha': date(2026, 11, 2),
        'responsable': f_acuaman.nombre if f_acuaman else 'Acuaman',
        'id_funcionario': f_acuaman,
        'id_delegacion': d_antena,
        'solicitante': 'Marcela Patricia Núñez',
        'rut': '12.789.456-2',
        'territorio': 'Sector El Brillador y Viña del Mar',
        'item': 'GESTIÓN TERRITORIAL Y OPERATIVOS',
        'solicitud': 'Operativo de desmalezado y perfilado de aceras en Villa Lambert',
        'accion': 'Cuadrilla municipal ejecutó corte de maleza y retiro.',
        'estado': 'En Proceso',
        'es_social': False,
        'ingreso_tubo': True,
        'compromiso': compromisos_creados[2],
        'estado_evidencia': 'En Revisión',
        'tipo_impacto': 'Cuantitativa',
        'obs_revision': 'Pendiente de revisión fotográfica por parte del supervisor.',
    },
    {
        'fecha': date(2026, 11, 2),
        'responsable': f_capamerica.nombre if f_capamerica else 'Capitán América',
        'id_funcionario': f_capamerica,
        'id_delegacion': d_rural,
        'solicitante': 'Fernando Javier Godoy',
        'rut': '15.432.109-8',
        'territorio': 'Sector Rural El Romero',
        'item': 'INFORMES SOCIALES Y FICHAS FIBE',
        'solicitud': 'Gestión de beneficio catastrófico y postulación habitacional',
        'accion': 'Ficha de protección y antecedentes en trámite.',
        'estado': 'En Proceso',
        'es_social': True,
        'ingreso_tubo': True,
        'compromiso': compromisos_creados[3],
        'estado_evidencia': 'Aprobada',
        'tipo_impacto': 'Cuantitativa',
        'obs_revision': 'Informe social emitido y antecedentes revisados correctamente.',
    },
    {
        'fecha': date(2026, 11, 1),
        'responsable': f_flash.nombre if f_flash else 'Flash',
        'id_funcionario': f_flash,
        'id_delegacion': d_comp,
        'solicitante': 'Mario Alberto Cortés',
        'rut': '16.543.210-9',
        'territorio': 'Sector Las Compañías Bajas',
        'item': 'ATENCIÓN SOCIAL Y RECEPCIÓN DE SOLICITUDES',
        'solicitud': 'Tramitación de subsidio de agua potable y canasta familiar',
        'accion': 'Recepción de antecedentes socioeconómicos y postulación en sistema.',
        'estado': 'En Proceso',
        'es_social': True,
        'ingreso_tubo': True,
        'compromiso': compromisos_creados[4],
        'estado_evidencia': 'Requiere Información',
        'tipo_impacto': 'Cuantitativa',
        'obs_revision': 'Se requiere fotografía nítida de boleta de agua y certificado de residencia emitido por junta de vecinos para validar postulación a subsidio.',
    },
    {
        'fecha': date(2026, 11, 1),
        'responsable': f_pantera.nombre if f_pantera else 'Pantera Negra',
        'id_funcionario': f_pantera,
        'id_delegacion': d_centro,
        'solicitante': 'Francisca Belén Santander',
        'rut': '11.876.543-9',
        'territorio': 'Sector Casco Histórico y Colina El Pino',
        'item': 'GESTIÓN TERRITORIAL Y OPERATIVOS',
        'solicitud': 'Levantamiento planimétrico de accesibilidad peatonal en Centro',
        'accion': 'Levantamiento topográfico en terreno.',
        'estado': 'En Proceso',
        'es_social': False,
        'ingreso_tubo': True,
        'compromiso': compromisos_creados[5],
        'estado_evidencia': 'Aprobada',
        'tipo_impacto': 'Cuantitativa',
        'obs_revision': 'Planimetría y levantamiento técnico validados.',
    },
    {
        'fecha': date(2026, 11, 1),
        'responsable': f_capmarvel.nombre if f_capmarvel else 'Capitana Marvel',
        'id_funcionario': f_capmarvel,
        'id_delegacion': d_rural,
        'solicitante': 'Silvia Inés Pastén',
        'rut': '18.234.567-1',
        'territorio': 'Sector Altovalsol y Las Rojas',
        'item': 'GESTIÓN TERRITORIAL Y OPERATIVOS',
        'solicitud': 'Poda preventiva y despeje de ramas sobre tendido eléctrico',
        'accion': 'Visita técnica conjunta con empresa eléctrica.',
        'estado': 'En Proceso',
        'es_social': False,
        'ingreso_tubo': True,
        'compromiso': compromisos_creados[6],
        'estado_evidencia': 'Aprobada',
        'tipo_impacto': 'Cuantitativa',
        'obs_revision': 'Coordinación con CGE y fotografías de terreno conformes.',
    },
    {
        'fecha': date(2026, 10, 30),
        'responsable': f_capmarvel.nombre if f_capmarvel else 'Capitana Marvel',
        'id_funcionario': f_capmarvel,
        'id_delegacion': d_rural,
        'solicitante': 'Oscar Armando Galleguillos',
        'rut': '15.432.109-8',
        'territorio': 'Sector Rural El Romero',
        'item': 'GESTIÓN TERRITORIAL Y OPERATIVOS',
        'solicitud': 'Operativo de retiro de voluminosos y limpieza en Quebrada',
        'accion': 'Operativo coordinado con tolva municipal y retiro de desechos.',
        'estado': 'Realizado',
        'es_social': False,
        'ingreso_tubo': True,
        'compromiso': compromisos_creados[7],
        'estado_evidencia': 'En Revisión',
        'tipo_impacto': 'Cuantitativa',
        'obs_revision': 'En revisión por supervisor para validar volumen retirado.',
    },
    {
        'fecha': date(2026, 10, 29),
        'responsable': f_acuaman.nombre if f_acuaman else 'Acuaman',
        'id_funcionario': f_acuaman,
        'id_delegacion': d_antena,
        'solicitante': 'Andrés Sebastián Barraza',
        'rut': '14.521.890-3',
        'territorio': 'Sector La Antena y Santa Inés',
        'item': 'GESTIÓN TERRITORIAL Y OPERATIVOS',
        'solicitud': 'Mantención y mejoramiento de luminarias LED en Calle 18 de Septiembre',
        'accion': 'Cuadrilla técnica reparó cableado y reemplazó focos averiados.',
        'estado': 'Realizado',
        'es_social': False,
        'ingreso_tubo': True,
        'compromiso': compromisos_creados[8],
        'estado_evidencia': 'Aprobada',
        'tipo_impacto': 'Cuantitativa',
        'obs_revision': 'Verificación de iluminación nocturna aprobada.',
    },
    {
        'fecha': date(2026, 10, 28),
        'responsable': f_spiderman.nombre if f_spiderman else 'Spider-Man',
        'id_funcionario': f_spiderman,
        'id_delegacion': d_comp,
        'solicitante': 'Juan Carlos Carvajal',
        'rut': '16.543.210-9',
        'territorio': 'Sector Las Compañías Bajas',
        'item': 'GESTIÓN TERRITORIAL Y OPERATIVOS',
        'solicitud': 'Reparación y reposición de luminarias LED viales en Las Compañías',
        'accion': 'Circuito de iluminación normalizado.',
        'estado': 'Realizado',
        'es_social': False,
        'ingreso_tubo': True,
        'compromiso': compromisos_creados[9],
        'estado_evidencia': 'Aprobada',
        'tipo_impacto': 'Cuantitativa',
        'obs_revision': 'Fotografía de luminaria encendida verificada.',
    },
    {
        'fecha': date(2026, 10, 28),
        'responsable': f_hulk.nombre if f_hulk else 'Hulk',
        'id_funcionario': f_hulk,
        'id_delegacion': d_centro,
        'solicitante': 'Raúl Hernán Castillo',
        'rut': '11.876.543-9',
        'territorio': 'Sector Casco Histórico y Colina El Pino',
        'item': 'VISITA A TERRENO Y PERITAJE',
        'solicitud': 'Visita de verificación social por vulnerabilidad de adulto mayor',
        'accion': 'Programación de visita en terreno para la próxima semana.',
        'estado': 'Pendiente',
        'es_social': True,
        'ingreso_tubo': True,
        'compromiso': compromisos_creados[10],
        'estado_evidencia': 'En Revisión',
        'tipo_impacto': 'Cuantitativa',
        'obs_revision': 'Expediente social en revisión preliminar.',
    },
    {
        'fecha': date(2026, 10, 27),
        'responsable': f_flash.nombre if f_flash else 'Flash',
        'id_funcionario': f_flash,
        'id_delegacion': d_comp,
        'solicitante': 'Teresa Silva Monardez',
        'rut': '14.238.901-2',
        'territorio': 'Sector Las Compañías Bajas',
        'item': 'SEGUIMIENTO CASOS DE ALTA COMPLEJIDAD',
        'solicitud': 'Visita domiciliaria urgente por situación de postración',
        'accion': 'Ficha de requerimiento de asistencia social abierta.',
        'estado': 'Pendiente',
        'es_social': True,
        'ingreso_tubo': True,
        'compromiso': compromisos_creados[11],
        'estado_evidencia': 'Aprobada',
        'tipo_impacto': 'Cuantitativa',
        'obs_revision': 'Caso social verificado y derivación médica realizada.',
    },
    {
        'fecha': date(2026, 10, 26),
        'responsable': f_spiderman.nombre if f_spiderman else 'Spider-Man',
        'id_funcionario': f_spiderman,
        'id_delegacion': d_antena,
        'solicitante': 'Lorena Andrea Vega',
        'rut': '13.904.551-8',
        'territorio': 'Sector La Antena y Santa Inés',
        'item': 'GESTIÓN TERRITORIAL Y OPERATIVOS',
        'solicitud': 'Retiro de escombros y ramas caídas en Plaza La Antena',
        'accion': 'Coordinación con personal de aseo y tolva municipal.',
        'estado': 'Pendiente',
        'es_social': False,
        'ingreso_tubo': True,
        'compromiso': compromisos_creados[12],
        'estado_evidencia': 'Requiere Información',
        'tipo_impacto': 'Cuantitativa',
        'obs_revision': 'Falta fotografía panorámica posterior al retiro de escombros para constatar despeje total del espacio público.',
    },
    # 11 Gestiones directas adicionales para totalizar 24
    {
        'fecha': date(2026, 11, 3),
        'responsable': f_capmarvel.nombre if f_capmarvel else 'Capitana Marvel',
        'id_funcionario': f_capmarvel,
        'id_delegacion': d_rural,
        'solicitante': 'Gonzalo Andrés Pizarro',
        'rut': '14.521.890-3',
        'territorio': 'Sector Altovalsol y Las Rojas',
        'item': 'GESTIÓN TERRITORIAL Y OPERATIVOS',
        'solicitud': 'Inspección de canal de regadío y despeje de compuertas en Las Rojas',
        'accion': 'Visita inspectiva conjunta con asociación de regantes.',
        'estado': 'Pendiente',
        'es_social': False,
        'ingreso_tubo': False,
        'compromiso': None,
        'estado_evidencia': 'Aprobada',
        'tipo_impacto': 'Cualitativa',
        'obs_revision': 'Gestión protocolar y de relacionamiento vecinal; se valida como cualitativa para registro formal sin ponderar a metas.',
    },
    {
        'fecha': date(2026, 11, 3),
        'responsable': f_pantera.nombre if f_pantera else 'Pantera Negra',
        'id_funcionario': f_pantera,
        'id_delegacion': d_centro,
        'solicitante': 'Cristián Eduardo Araya',
        'rut': '11.876.543-9',
        'territorio': 'Sector Casco Histórico y Colina El Pino',
        'item': 'GESTIÓN TERRITORIAL Y OPERATIVOS',
        'solicitud': 'Fiscalización de ocupación de veredas y comercio no autorizado en Centro',
        'accion': 'Plan de fiscalización en coordinación con Seguridad Ciudadana.',
        'estado': 'Pendiente',
        'es_social': False,
        'ingreso_tubo': False,
        'compromiso': None,
        'estado_evidencia': 'Aprobada',
        'tipo_impacto': 'Cuantitativa',
        'obs_revision': 'Acta de fiscalización comunal recepcionada.',
    },
    {
        'fecha': date(2026, 11, 3),
        'responsable': f_capamerica.nombre if f_capamerica else 'Capitán América',
        'id_funcionario': f_capamerica,
        'id_delegacion': d_antena,
        'solicitante': 'Paola Verónica Zepeda',
        'rut': '13.904.551-8',
        'territorio': 'Sector La Antena y Santa Inés',
        'item': 'INFORMES SOCIALES Y FICHAS FIBE',
        'solicitud': 'Aplicación de Ficha Básica de Emergencia comunal por anegamiento',
        'accion': 'Ficha FIBE levantada y registrada en plataforma social.',
        'estado': 'Pendiente',
        'es_social': True,
        'ingreso_tubo': False,
        'compromiso': None,
        'estado_evidencia': 'Aprobada',
        'tipo_impacto': 'Cuantitativa',
        'obs_revision': 'Ficha FIBE validada con firma digital del gestor social.',
    },
    {
        'fecha': date(2026, 11, 3),
        'responsable': f_acuaman.nombre if f_acuaman else 'Acuaman',
        'id_funcionario': f_acuaman,
        'id_delegacion': d_antena,
        'solicitante': 'Patricio Rojas Castro',
        'rut': '15.312.890-4',
        'territorio': 'Sector La Antena y Santa Inés',
        'item': 'GESTIÓN TERRITORIAL Y OPERATIVOS',
        'solicitud': 'Instalación de señalética de zona escolar y cruces peatonales',
        'accion': 'Requerimiento técnico verificado e ingresado a taller vial.',
        'estado': 'Pendiente',
        'es_social': False,
        'ingreso_tubo': False,
        'compromiso': None,
        'estado_evidencia': 'Requiere Información',
        'tipo_impacto': 'Cuantitativa',
        'obs_revision': 'Falta esquema técnico de demarcación vial emitido por la Dirección de Tránsito antes de validar.',
    },
    {
        'fecha': date(2026, 11, 3),
        'responsable': f_heman.nombre if f_heman else 'He-Man',
        'id_funcionario': f_heman,
        'id_delegacion': d_comp,
        'solicitante': 'Esteban Pizarro Campusano',
        'rut': '14.238.901-2',
        'territorio': 'Sector Las Compañías Bajas',
        'item': 'EMERGENCIAS COMUNALES Y REUNIONES',
        'solicitud': 'Mesa técnica por proyecto de pavimentación participativa con JJVV',
        'accion': 'Acta de acuerdos y cronograma de pavimentación validado.',
        'estado': 'Pendiente',
        'es_social': False,
        'ingreso_tubo': False,
        'compromiso': None,
        'estado_evidencia': 'En Revisión',
        'tipo_impacto': 'Cualitativa',
        'obs_revision': 'Mesa técnica informativa en revisión.',
    },
    {
        'fecha': date(2026, 11, 2),
        'responsable': f_hulk.nombre if f_hulk else 'Hulk',
        'id_funcionario': f_hulk,
        'id_delegacion': d_centro,
        'solicitante': 'Valeria Soledad Pinto',
        'rut': '11.876.543-9',
        'territorio': 'Sector Balmaceda y La Pampa',
        'item': 'ATENCIÓN SOCIAL A USUARIO PRESENCIAL',
        'solicitud': 'Orientación de subsidio habitacional y ficha social de postulación',
        'accion': 'Orientación técnica brindada en ventanilla y ficha social abierta.',
        'estado': 'En Proceso',
        'es_social': True,
        'ingreso_tubo': False,
        'compromiso': None,
        'estado_evidencia': 'Aprobada',
        'tipo_impacto': 'Cuantitativa',
        'obs_revision': 'Atención presencial registrada con cartola RSH adjunta.',
    },
    {
        'fecha': date(2026, 10, 31),
        'responsable': f_capamerica.nombre if f_capamerica else 'Capitán América',
        'id_funcionario': f_capamerica,
        'id_delegacion': d_antena,
        'solicitante': 'Mónica Andrea Espinoza',
        'rut': '13.904.551-8',
        'territorio': 'Sector La Antena y Santa Inés',
        'item': 'ATENCIÓN DE USUARIO PRESENCIAL Y TELEFÓNICA',
        'solicitud': 'Actualización de Registro Social de Hogares por cambio de domicilio',
        'accion': 'Trámite RSH completado y cartola emitida.',
        'estado': 'Realizado',
        'es_social': False,
        'ingreso_tubo': False,
        'compromiso': None,
        'estado_evidencia': 'Aprobada',
        'tipo_impacto': 'Cuantitativa',
        'obs_revision': 'Cartola RSH generada y archivada correctamente.',
    },
    {
        'fecha': date(2026, 10, 30),
        'responsable': f_pantera.nombre if f_pantera else 'Pantera Negra',
        'id_funcionario': f_pantera,
        'id_delegacion': d_centro,
        'solicitante': 'Manuel Alejandro Cerda',
        'rut': '12.789.456-2',
        'territorio': 'Sector Casco Histórico y Colina El Pino',
        'item': 'GESTIÓN TERRITORIAL Y OPERATIVOS',
        'solicitud': 'Auditoría e inspección técnica de señalética turística patrimonial',
        'accion': 'Informe de reposición y catastro de letreros dañado emitido.',
        'estado': 'Realizado',
        'es_social': False,
        'ingreso_tubo': False,
        'compromiso': None,
        'estado_evidencia': 'Aprobada',
        'tipo_impacto': 'Cuantitativa',
        'obs_revision': 'Catastro de señalética verificado conforme a norma patrimonial.',
    },
    {
        'fecha': date(2026, 10, 30),
        'responsable': f_flash.nombre if f_flash else 'Flash',
        'id_funcionario': f_flash,
        'id_delegacion': d_comp,
        'solicitante': 'Gladys del Carmen Ramos',
        'rut': '16.543.210-9',
        'territorio': 'Sector Las Compañías Bajas',
        'item': 'VISITAS DOMICILIARIAS Y FICHA FIBE',
        'solicitud': 'Evaluación socioeconómica y ficha de protección a grupo familiar',
        'accion': 'Visita domiciliaria realizada e informe emitido.',
        'estado': 'Realizado',
        'es_social': True,
        'ingreso_tubo': False,
        'compromiso': None,
        'estado_evidencia': 'Aprobada',
        'tipo_impacto': 'Cuantitativa',
        'obs_revision': 'Informe socioeconómico aprobado por jefatura técnica.',
    },
    {
        'fecha': date(2026, 10, 29),
        'responsable': f_hulk.nombre if f_hulk else 'Hulk',
        'id_funcionario': f_hulk,
        'id_delegacion': d_centro,
        'solicitante': 'Jorge Antonio Miranda',
        'rut': '11.876.543-9',
        'territorio': 'Sector Casco Histórico y Colina El Pino',
        'item': 'EMERGENCIA SOCIAL INMEDIATA',
        'solicitud': 'Asistencia integral a persona en situación de calle y albergue',
        'accion': 'Derivación y acogida en red de apoyo social municipal.',
        'estado': 'Realizado',
        'es_social': True,
        'ingreso_tubo': False,
        'compromiso': None,
        'estado_evidencia': 'Aprobada',
        'tipo_impacto': 'Cuantitativa',
        'obs_revision': 'Derivación efectiva a albergue municipal confirmada.',
    },
    {
        'fecha': date(2026, 10, 29),
        'responsable': f_heman.nombre if f_heman else 'He-Man',
        'id_funcionario': f_heman,
        'id_delegacion': d_comp,
        'solicitante': 'Rodrigo Morales Araya',
        'rut': '14.238.901-2',
        'territorio': 'Sector El Brillador y Viña del Mar',
        'item': 'EMERGENCIAS COMUNALES Y REUNIONES',
        'solicitud': 'Mesa barrial de seguridad y luminarias en sede vecinal',
        'accion': 'Coordinación con dirigentes vecinales y Carabineros ejecutada.',
        'estado': 'Realizado',
        'es_social': False,
        'ingreso_tubo': False,
        'compromiso': None,
        'estado_evidencia': 'Aprobada',
        'tipo_impacto': 'Cuantitativa',
        'obs_revision': 'Acta de mesa barrial con nómina de asistencia verificada.',
    },
]

admin_u = User.objects.filter(username='admin').first()
gestiones_creadas = []
for gd in gestiones_datos:
    est_evi = gd.get('estado_evidencia', 'Aprobada')
    tipo_imp = gd.get('tipo_impacto', 'Cuantitativa')
    obs_rev = gd.get('obs_revision', '')
    revisor = admin_u if est_evi in ['Aprobada', 'Requiere Información', 'Rechazada'] else None
    f_rev = timezone.now() if revisor else None

    act = Actividad.objects.create(
        fecha=gd['fecha'],
        responsable=gd['responsable'],
        id_funcionario=gd['id_funcionario'],
        id_delegacion=gd['id_delegacion'],
        solicitante=gd['solicitante'],
        contacto=gd['solicitante'],
        rut_solicitante=gd['rut'],
        territorio=gd['territorio'],
        item_evaluacion=gd['item'],
        solicitud=gd['solicitud'],
        accion=gd['accion'],
        estado=gd['estado'],
        es_gestion_social=gd['es_social'],
        ingreso_tubo=gd['ingreso_tubo'],
        id_compromiso=gd['compromiso'],
        id_tipo=tipo_soc if gd['es_social'] else tipo_ter,
        id_subatencion=sub_soc if gd['es_social'] else sub_ter,
        usuario_creador=gd['id_funcionario'].user if gd['id_funcionario'] and gd['id_funcionario'].user else None,
        estado_evidencia=est_evi,
        tipo_impacto=tipo_imp,
        observacion_revision=obs_rev,
        fecha_revision=f_rev,
        usuario_revisor=revisor,
    )
    if gd.get('compromiso'):
        comp_obj = gd['compromiso']
        comp_obj.id_actividad = act
        comp_obj.save(update_fields=['id_actividad'])
    gestiones_creadas.append(act)

print(f"[OK] {len(gestiones_creadas)} Gestiones Unificadas creadas (exactamente 24).")

# 12. Creacion de Atenciones Ciudadanas (4 registros - 1 por delegacion)
admin_u = User.objects.filter(username='admin').first()
atenciones_datos = [
    {
        'vecino': vecinos_dict['14.521.890-3'],
        'del': d_antena,
        'tipo': tipo_soc,
        'sub': sub_soc,
        'desc': 'Consulta sobre postulación a subsidios de vivienda DS49 y actualización de RSH.',
        'est': 'Resuelto'
    },
    {
        'vecino': vecinos_dict['16.543.210-9'],
        'del': d_comp,
        'tipo': tipo_ter,
        'sub': sub_ter,
        'desc': 'Requerimiento de poda de árbol que interfiere con cables en Calle Esmeralda.',
        'est': 'Derivado'
    },
    {
        'vecino': vecinos_dict['11.876.543-9'],
        'del': d_centro,
        'tipo': tipo_ter,
        'sub': sub_ter,
        'desc': 'Solicitud de mayor presencia de patrullaje de seguridad en Casco Histórico nocturno.',
        'est': 'En Trámite'
    },
    {
        'vecino': vecinos_dict['15.432.109-8'],
        'del': d_rural,
        'tipo': tipo_soc,
        'sub': sub_soc,
        'desc': 'Solicitud de asistencia médica y entrega de medicamentos para adulto mayor postrado.',
        'est': 'Resuelto'
    },
]

for ad in atenciones_datos:
    v = ad['vecino']
    AtencionCiudadana.objects.create(
        id_vecino=v,
        solicitante=v.nombre,
        rut_solicitante=v.rut,
        telefono=v.telefono,
        correo=v.correo,
        direccion=v.direccion,
        id_delegacion=ad['del'],
        id_tipo=ad['tipo'],
        id_subatencion=ad['sub'],
        descripcion=ad['desc'],
        estado=ad['est'],
        id_usuario_responsable=admin_u
    )

print(f"[OK] {len(atenciones_datos)} Atenciones Ciudadanas creadas.")

# 13. Creacion de Fichas de Gestor Social (2 casos)
sociales_datos = [
    {
        'usuario': 'Marcela Patricia Núñez',
        'rut': '12.789.456-2',
        'telefono': '+56 9 7890 1234',
        'direccion': 'Calle Balmaceda #1458, La Serena',
        'tipo': tipo_soc,
        'sub': sub_soc,
        'visita': True,
        'f_visita': date(2026, 10, 22),
        'f_prog': date(2026, 10, 20),
        'obs': 'Adulto mayor en situación de vulnerabilidad con daño estructural en techumbre por lluvias.',
        'g1': 'ATENCIÓN SOCIAL A USUARIO PRESENCIAL',
        'g2': 'VISITA TERRENO E INFORME FIBE',
        'g3': 'ENTREGA BENEFICIO Y MATERIALES',
        'f_inf': date(2026, 10, 25),
        'f_ben': date(2026, 10, 29),
        'est': 'En Proceso',
    },
    {
        'usuario': 'Valeria Soledad Pinto',
        'rut': '11.876.543-9',
        'telefono': '+56 9 8901 2345',
        'direccion': 'Calle Los Carrera #340, Centro',
        'tipo': tipo_soc,
        'sub': sub_soc,
        'visita': True,
        'f_visita': date(2026, 10, 28),
        'f_prog': date(2026, 10, 27),
        'obs': 'Caso social derivado por junta de vecinos. Requiere apoyo paliativo y canasta de alimentos.',
        'g1': 'ATENCIÓN SOCIAL A USUARIO PRESENCIAL',
        'g2': 'VISITA TERRENO E INFORME FIBE',
        'g3': 'ENTREGA BENEFICIO Y MATERIALES',
        'f_inf': date(2026, 10, 30),
        'f_ben': date(2026, 11, 2),
        'est': 'Resuelto',
    },
]

for sd in sociales_datos:
    GestionSocial.objects.create(
        fecha_ingreso=date(2026, 10, 20),
        id_tipo=sd['tipo'],
        id_subatencion=sd['sub'],
        usuario=sd['usuario'],
        rut=sd['rut'],
        telefono=sd['telefono'],
        direccion=sd['direccion'],
        requiere_visita=sd['visita'],
        fecha_programada_visita=sd['f_prog'],
        fecha_visita=sd['f_visita'],
        observaciones=sd['obs'],
        primera_gestion=sd['g1'],
        segunda_gestion=sd['g2'],
        tercera_gestion=sd['g3'],
        fecha_entrega_informe=sd['f_inf'],
        fecha_entrega_beneficio=sd['f_ben'],
        estado=sd['est'],
        ingreso_tubo=False,
        id_funcionario=f_flash,
        id_delegacion=d_comp
    )

print(f"[OK] {len(sociales_datos)} Casos de Gestor Social creados.")

# 14. Indicadores de Delegacion (4 delegaciones para Q4 2026)
indicadores_datos = [
    {'del': d_comp, 'area': 'Área Territorial y Comunitaria', 'resp': 'He-Man', 'av': Decimal('88.5'), 'lic': 2, 'vac': 3, 'em': 1, 'comp': 1},
    {'del': d_antena, 'area': 'Área Social y Operaciones', 'resp': 'Thor', 'av': Decimal('91.2'), 'lic': 1, 'vac': 2, 'em': 2, 'comp': 0},
    {'del': d_centro, 'area': 'Área Centro y Casco Histórico', 'resp': 'Batman', 'av': Decimal('84.0'), 'lic': 3, 'vac': 1, 'em': 0, 'comp': 2},
    {'del': d_rural, 'area': 'Área Valles y Cuenca Rural', 'resp': 'Superman', 'av': Decimal('86.7'), 'lic': 1, 'vac': 2, 'em': 1, 'comp': 1},
]

for idata in indicadores_datos:
    IndicadorDelegacion.objects.create(
        id_delegacion=idata['del'],
        id_periodo=p4,
        area=idata['area'],
        responsable=idata['resp'],
        avance_porcentaje=idata['av'],
        licencias=idata['lic'],
        vacaciones=idata['vac'],
        emergencias=idata['em'],
        compensatorios=idata['comp']
    )

print(f"[OK] {len(indicadores_datos)} Indicadores de Delegación creados para el 4to Trimestre 2026.")

print("\n--- REPOBLAMIENTO COMPLETADO EXITOSAMENTE ---")
print(f"Total Gestiones Base: {Actividad.objects.filter(id_gestion_padre__isnull=True).count()} (esperado 24)")
print(f"Total Compromisos Base: {Compromiso.objects.count()} (esperado 13)")
print(f"Total Metas Base: {MetaFuncionario.objects.count()} (16 metas en 4to Trimestre 2026)")
