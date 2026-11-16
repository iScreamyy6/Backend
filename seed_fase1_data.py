"""
Script para poblar registros institucionales de ejemplo para Territorios, Juntas de Vecinos y Directivas
en la Ilustre Municipalidad de La Serena.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Municipalidad.settings')
django.setup()

from datetime import date
from organizacion.models import Delegacion, Territorio, JuntaVecinos, ParticipacionJunta
from actividades.models import Vecino

# 1. Obtener Delegaciones
d_comp = Delegacion.objects.filter(codigo='D01').first() or Delegacion.objects.get(pk=1)
d_antena = Delegacion.objects.filter(codigo='D02').first() or Delegacion.objects.get(pk=2)
d_centro = Delegacion.objects.filter(codigo='D03').first() or Delegacion.objects.get(pk=3)
d_rural = Delegacion.objects.filter(codigo='D04').first() or Delegacion.objects.get(pk=4)

print(f"Delegaciones cargadas: {d_comp.nombre}, {d_antena.nombre}, {d_centro.nombre}, {d_rural.nombre}")

# 2. Territorios de Ejemplo
territorios_data = [
    # La Antena (D02)
    {
        'nombre': 'Sector La Antena y Santa Inés',
        'delegacion': d_antena,
        'descripcion': 'Sector histórico de La Antena, colindante con Santa Inés y subida 18 de Septiembre.',
        'estado': 'Activo'
    },
    {
        'nombre': 'Sector La Florida y Pan de Azúcar Urbano',
        'delegacion': d_antena,
        'descripcion': 'Cuadrante residencial de La Florida alta, Villa El Indio y accesos a Ruta D-41.',
        'estado': 'Activo'
    },
    {
        'nombre': 'Sector San Joaquín y El Milagro',
        'delegacion': d_antena,
        'descripcion': 'Sectores residenciales de San Joaquín, El Milagro I y II, y Lomas de San Joaquín.',
        'estado': 'Activo'
    },
    # Centro y Casco Histórico (D03)
    {
        'nombre': 'Sector Colina El Pino y Cerro Grande',
        'delegacion': d_centro,
        'descripcion': 'Zona residencial y universitaria de La Colina, campus Andrés Bello y faldeos poniente de Cerro Grande.',
        'estado': 'Activo'
    },
    # Las Compañías (D01)
    {
        'nombre': 'Sector El Brillador y Viña del Mar',
        'delegacion': d_comp,
        'descripcion': 'Eje norte de Las Compañías, sectores El Brillador, Villa Lambert y Villa Viña del Mar.',
        'estado': 'Activo'
    },
    # Rural (D04)
    {
        'nombre': 'Sector Altovalsol y Las Rojas',
        'delegacion': d_rural,
        'descripcion': 'Cuenca media del Río Elqui, pueblos rurales tradicionales de Altovalsol, Las Rojas y Quebrada de Talca.',
        'estado': 'Activo'
    },
    {
        'nombre': 'Sector El Romero y Coquimbito',
        'delegacion': d_rural,
        'descripcion': 'Franja agrícola norte del valle, comunidades de El Romero, Coquimbito y La Estrella.',
        'estado': 'Activo'
    },
]

territorios_creados = {}
for td in territorios_data:
    t, created = Territorio.objects.get_or_create(
        nombre=td['nombre'],
        delegacion=td['delegacion'],
        defaults={
            'descripcion': td['descripcion'],
            'estado': td['estado']
        }
    )
    territorios_creados[t.nombre] = t
    status = "CREADO" if created else "EXISTE"
    print(f"[{status}] Territorio: [{t.codigo}] {t.nombre} ({t.delegacion.nombre})")

# 3. Juntas de Vecinos de Ejemplo
juntas_data = [
    # La Antena
    {
        'nombre': "Junta de Vecinos Bernardo O'Higgins de La Antena",
        'direccion': 'Calle 18 de Septiembre #450, La Antena',
        'delegacion': d_antena,
        'territorio_nombre': 'Sector La Antena y Santa Inés',
        'fecha_constitucion': date(1988, 5, 12),
        'estado': 'Activa'
    },
    {
        'nombre': 'Junta de Vecinos Villa El Indio',
        'direccion': 'Pasaje Los Conquistadores #120, La Florida',
        'delegacion': d_antena,
        'territorio_nombre': 'Sector La Florida y Pan de Azúcar Urbano',
        'fecha_constitucion': date(1994, 8, 24),
        'estado': 'Activa'
    },
    {
        'nombre': 'Junta de Vecinos El Milagro Oriente',
        'direccion': 'Av. Alberto Arenas #2200, El Milagro',
        'delegacion': d_antena,
        'territorio_nombre': 'Sector San Joaquín y El Milagro',
        'fecha_constitucion': date(2005, 10, 15),
        'estado': 'Activa'
    },
    # Centro
    {
        'nombre': 'Junta de Vecinos Alborada - Balmaceda',
        'direccion': 'Calle Balmaceda #1450, Sector Pampa',
        'delegacion': d_centro,
        'territorio_nombre': 'Sector Balmaceda y Pampa',
        'fecha_constitucion': date(1991, 4, 3),
        'estado': 'Activa'
    },
    {
        'nombre': 'Junta de Vecinos Colina El Pino',
        'direccion': 'Pasaje Los Aromos #310, La Colina',
        'delegacion': d_centro,
        'territorio_nombre': 'Sector Colina El Pino y Cerro Grande',
        'fecha_constitucion': date(1999, 11, 20),
        'estado': 'Activa'
    },
    # Las Compañías
    {
        'nombre': 'Junta de Vecinos Villa San Bartolomé',
        'direccion': 'Calle Esmeralda #340, Las Compañías Bajas',
        'delegacion': d_comp,
        'territorio_nombre': 'Las Compañías Bajas',
        'fecha_constitucion': date(1996, 6, 10),
        'estado': 'Activa'
    },
    {
        'nombre': 'Junta de Vecinos El Brillador Alto',
        'direccion': 'Pasaje La Mina #88, Las Compañías',
        'delegacion': d_comp,
        'territorio_nombre': 'Sector El Brillador y Viña del Mar',
        'fecha_constitucion': date(2001, 9, 8),
        'estado': 'Activa'
    },
    # Rural
    {
        'nombre': 'Junta de Vecinos Las Rojas Centro',
        'direccion': 'Calle Principal s/n, Pueblo de Las Rojas',
        'delegacion': d_rural,
        'territorio_nombre': 'Sector Altovalsol y Las Rojas',
        'fecha_constitucion': date(1985, 3, 14),
        'estado': 'Activa'
    },
    {
        'nombre': 'Comité Vecinal El Romero',
        'direccion': 'Camino Vecinal El Romero Lote 4',
        'delegacion': d_rural,
        'territorio_nombre': 'Sector El Romero y Coquimbito',
        'fecha_constitucion': date(1998, 7, 29),
        'estado': 'Activa'
    },
]

juntas_creadas = {}
for jd in juntas_data:
    ter = Territorio.objects.filter(nombre=jd['territorio_nombre']).first()
    j, created = JuntaVecinos.objects.get_or_create(
        nombre=jd['nombre'],
        delegacion=jd['delegacion'],
        defaults={
            'direccion': jd['direccion'],
            'territorio': ter,
            'fecha_constitucion': jd['fecha_constitucion'],
            'estado': jd['estado']
        }
    )
    if not created and ter and j.territorio != ter:
        j.territorio = ter
        j.save()
    juntas_creadas[j.nombre] = j
    status = "CREADO" if created else "EXISTE"
    print(f"[{status}] Junta de Vecinos: [{j.codigo}] {j.nombre} ({j.delegacion.nombre})")

# 4. Asegurar vecinos adicionales para asignar directivas
vecinos_extra = [
    {
        'rut': '17.842.119-3',
        'nombre': 'Guillermo Cortés Núñez',
        'telefono': '+56 9 8452 1109',
        'correo': 'guillermo.cortes@correo.cl',
        'direccion': 'Calle 18 de Septiembre #450, La Antena',
        'territorio': 'Sector La Antena y Santa Inés'
    },
    {
        'rut': '13.904.551-8',
        'nombre': 'Lorena Patricia Carmona Díaz',
        'telefono': '+56 9 7611 2345',
        'correo': 'lorena.carmona@correo.cl',
        'direccion': 'Pasaje Los Conquistadores #124, La Florida',
        'territorio': 'Sector La Florida y Pan de Azúcar Urbano'
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
        'rut': '11.654.321-7',
        'nombre': 'Marta Henríquez Rivera',
        'telefono': '+56 9 8234 5678',
        'correo': 'marta.henriquez@correo.cl',
        'direccion': 'Calle Balmaceda #1458, La Serena',
        'territorio': 'Sector Balmaceda y Pampa'
    },
    {
        'rut': '18.234.567-1',
        'nombre': 'Esteban Andrés Munizaga Morales',
        'telefono': '+56 9 6543 2198',
        'correo': 'esteban.munizaga@correo.cl',
        'direccion': 'Calle Principal s/n, Las Rojas',
        'territorio': 'Sector Altovalsol y Las Rojas'
    },
]

vecinos_obj = {}
for vd in vecinos_extra:
    v, created = Vecino.objects.get_or_create(
        rut=vd['rut'],
        defaults={
            'nombre': vd['nombre'],
            'telefono': vd['telefono'],
            'correo': vd['correo'],
            'direccion': vd['direccion'],
            'territorio': vd['territorio']
        }
    )
    vecinos_obj[v.rut] = v
    status = "CREADO" if created else "EXISTE"
    print(f"[{status}] Vecino: {v.nombre} ({v.rut})")

# 5. Asignar directivas representativas a las juntas
directivas_data = [
    {
        'junta_nombre': "Junta de Vecinos Bernardo O'Higgins de La Antena",
        'vecino_rut': '17.842.119-3',
        'cargo': 'Presidente/a',
        'es_dirigente': True,
        'fecha': date(2024, 6, 1)
    },
    {
        'junta_nombre': "Junta de Vecinos Bernardo O'Higgins de La Antena",
        'vecino_rut': '16.543.210-9', # Juana de Lourdes Rojas Pérez
        'cargo': 'Secretario/a',
        'es_dirigente': True,
        'fecha': date(2024, 6, 1)
    },
    {
        'junta_nombre': 'Junta de Vecinos Villa El Indio',
        'vecino_rut': '13.904.551-8',
        'cargo': 'Presidente/a',
        'es_dirigente': True,
        'fecha': date(2023, 9, 15)
    },
    {
        'junta_nombre': 'Junta de Vecinos El Milagro Oriente',
        'vecino_rut': '15.312.890-4',
        'cargo': 'Presidente/a',
        'es_dirigente': True,
        'fecha': date(2024, 1, 10)
    },
    {
        'junta_nombre': 'Junta de Vecinos Alborada - Balmaceda',
        'vecino_rut': '11.654.321-7',
        'cargo': 'Presidente/a',
        'es_dirigente': True,
        'fecha': date(2023, 11, 20)
    },
    {
        'junta_nombre': 'Junta de Vecinos Las Rojas Centro',
        'vecino_rut': '18.234.567-1',
        'cargo': 'Presidente/a',
        'es_dirigente': True,
        'fecha': date(2024, 3, 5)
    },
    {
        'junta_nombre': 'Comité Vecinal El Romero',
        'vecino_rut': '14.223.344-5', # Beatriz Ossa Manríquez
        'cargo': 'Presidente/a',
        'es_dirigente': True,
        'fecha': date(2023, 5, 18)
    },
    {
        'junta_nombre': 'Junta de Vecinos Villa El Parque',
        'vecino_rut': '14.238.901-2', # María Elena González Silva
        'cargo': 'Presidente/a',
        'es_dirigente': True,
        'fecha': date(2024, 4, 12)
    },
    {
        'junta_nombre': 'Junta de Vecinos Villa El Parque',
        'vecino_rut': '9.988.776-6', # Rosa Valenzuela
        'cargo': 'Tesorero/a',
        'es_dirigente': True,
        'fecha': date(2024, 4, 12)
    },
    {
        'junta_nombre': 'Unión Vecinal Casco Histórico',
        'vecino_rut': '15.987.654-3', # Pedro Almonte Valdés
        'cargo': 'Director/a',
        'es_dirigente': True,
        'fecha': date(2024, 2, 1)
    },
]

for dd in directivas_data:
    j = JuntaVecinos.objects.filter(nombre=dd['junta_nombre']).first()
    v = Vecino.objects.filter(rut=dd['vecino_rut']).first()
    if j and v:
        p, created = ParticipacionJunta.objects.get_or_create(
            vecino=v,
            junta=j,
            defaults={
                'cargo': dd['cargo'],
                'es_dirigente': dd['es_dirigente'],
                'fecha_incorporacion': dd['fecha'],
                'estado': 'Activo'
            }
        )
        status = "CREADO" if created else "EXISTE"
        print(f"[{status}] Dirigente: {v.nombre} -> {dd['cargo']} en {j.nombre}")

# 6. Periodos de Evaluación y Trimestres SGR
from resultados.models import PeriodoEvaluacion, MetaFuncionario
from decimal import Decimal
from organizacion.models import Funcionario

p3 = PeriodoEvaluacion.objects.filter(pk=1).first() or PeriodoEvaluacion.objects.create(
    nombre='3er Trimestre 2026',
    fecha_inicio=date(2026, 7, 1),
    fecha_cierre=date(2026, 9, 30),
    dias_totales=92,
    dias_transcurridos=89,
    activo=True
)
p4, _ = PeriodoEvaluacion.objects.get_or_create(
    nombre='4to Trimestre 2026',
    defaults={
        'fecha_inicio': date(2026, 10, 1),
        'fecha_cierre': date(2026, 12, 31),
        'dias_totales': 92,
        'dias_transcurridos': 45,
        'activo': True
    }
)
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

# 7. Asignar Metas de ejemplo para Funcionario Flash (Total 100.00%)
f_flash = Funcionario.objects.filter(nombre__icontains='Flash').first()
if f_flash and p4:
    metas_flash = [
        {'item': 'ATENCIÓN SOCIAL Y RECEPCIÓN DE SOLICITUDES', 'ponderador': Decimal('30.00'), 'meta': 45},
        {'item': 'VISITAS DOMICILIARIAS Y FICHA FIBE', 'ponderador': Decimal('35.00'), 'meta': 30},
        {'item': 'GESTIÓN DE AYUDAS SOCIALES PALIATIVAS', 'ponderador': Decimal('20.00'), 'meta': 25},
        {'item': 'SEGUIMIENTO CASOS DE ALTA COMPLEJIDAD', 'ponderador': Decimal('15.00'), 'meta': 10},
    ]
    for mf in metas_flash:
        m, created = MetaFuncionario.objects.get_or_create(
            id_funcionario=f_flash,
            id_periodo=p4,
            item=mf['item'],
            defaults={
                'usuario_registro': f_flash.user,
                'ponderador': mf['ponderador'],
                'meta_periodo': mf['meta'],
                'avance_actual': 0
            }
        )
        status = "CREADO" if created else "EXISTE"
        print(f"[{status}] Meta Funcionario: {f_flash.nombre} -> {mf['item']} ({mf['ponderador']}%, Meta: {mf['meta']})")

print("\n[OK] Datos de ejemplo para Territorios, Juntas de Vecinos y Asignación de Metas poblados exitosamente.")
