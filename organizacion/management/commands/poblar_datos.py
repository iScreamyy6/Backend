import datetime
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from organizacion.models import Delegacion, Funcionario, Rol, PerfilUsuario, CargoTipoGestion
from actividades.models import Actividad, Evidencia, TipoAtencion, SubAtencion, AtencionCiudadana, Vecino
from agenda.models import Compromiso
from resultados.models import PeriodoEvaluacion, MetaFuncionario, IndicadorDelegacion, ItemMeta


class Command(BaseCommand):
    help = 'Pobla la base de datos con información inicial del SGR (Ilustre Municipalidad de La Serena)'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.NOTICE('Iniciando poblamiento de datos...'))

        # 1. Roles del Sistema
        roles_data = [
            {
                'codigo': 'ROL-ADM',
                'nombre': 'Administrador General',
                'descripcion': 'Acceso total y configuración comunal transversal',
                'alcance_autorizado': 'COMUNAL',
                'permisos': 'Crear, Editar, Consultar, Listar, Desactivar, Exportar, Configuración',
            },
            {
                'codigo': 'ROL-COORD',
                'nombre': 'Coordinador Municipal',
                'descripcion': 'Supervisión transversal y monitoreo de compromisos comunales',
                'alcance_autorizado': 'COMUNAL',
                'permisos': 'Consultar, Listar, Exportar, Monitoreo Metas',
            },
            {
                'codigo': 'ROL-DEL',
                'nombre': 'Delegado Municipal',
                'descripcion': 'Gestión y jefatura de delegación territorial asignada',
                'alcance_autorizado': 'DELEGACION',
                'permisos': 'Crear, Editar, Consultar, Listar, Exportar, Gestión Local',
            },
            {
                'codigo': 'ROL-OPE',
                'nombre': 'Funcionario Operador',
                'descripcion': 'Atención ciudadana, registro de casos y gestiones en terreno',
                'alcance_autorizado': 'DELEGACION',
                'permisos': 'Crear Atención, Consultar, Listar Gestiones',
            },
            {
                'codigo': 'ROL-VERIF',
                'nombre': 'Verificador Técnico',
                'descripcion': 'Auditoría y validación de evidencias fotográficas',
                'alcance_autorizado': 'DELEGACION',
                'permisos': 'Consultar, Validar Evidencias',
            },
        ]

        roles_objs = {}
        for r in roles_data:
            obj, _ = Rol.objects.update_or_create(
                codigo=r['codigo'],
                defaults={
                    'nombre': r['nombre'],
                    'descripcion': r['descripcion'],
                    'alcance_autorizado': r['alcance_autorizado'],
                    'permisos': r['permisos'],
                    'estado': 'Activo',
                }
            )
            roles_objs[r['codigo']] = obj
        self.stdout.write(self.style.SUCCESS(f'Roles creados/actualizados: {len(roles_objs)}'))

        # 2. Delegaciones
        delegaciones_data = [
            {
                'id': 1,
                'codigo': 'D01',
                'nombre': 'Delegación Municipal Las Compañías',
                'direccion': 'Esmeralda #2422, Las Compañías',
                'comuna': 'La Serena',
                'ambito': 'Las Compañías Alta y Baja',
                'responsable': 'He-Man',
                'foco_estrategico': 'Atención integral comunitaria, operativos sociales y resolución territorial rápida',
                'estado': 'Activa'
            },
            {
                'id': 2,
                'codigo': 'D02',
                'nombre': 'Delegación Municipal La Antena',
                'direccion': '12 de Octubre #1255, La Antena',
                'comuna': 'La Serena',
                'ambito': 'Sector La Antena y Florida',
                'responsable': 'Thor',
                'foco_estrategico': 'Seguridad vecinal, recuperación de espacios públicos y mediación comunitaria',
                'estado': 'Activa'
            },
            {
                'id': 3,
                'codigo': 'D03',
                'nombre': 'Delegación Municipal Centro y Casco Histórico',
                'direccion': 'Los Carrera #301, Centro',
                'comuna': 'La Serena',
                'ambito': 'Centro Urbano y Casco Histórico',
                'responsable': 'Batman',
                'foco_estrategico': 'Fiscalización comercial, turismo patrimonial y aseo urbano',
                'estado': 'Activa'
            },
            {
                'id': 4,
                'codigo': 'D04',
                'nombre': 'Delegación Municipal Rural',
                'direccion': 'Ruta D-41 Km 15, El Arrayán',
                'comuna': 'La Serena',
                'ambito': 'Valles y Localidades Rurales',
                'responsable': 'Superman',
                'foco_estrategico': 'Conectividad hídrica, caminos rurales y apoyo a crianceros',
                'estado': 'Activa'
            },
        ]

        delegacion_objs = {}
        for d in delegaciones_data:
            obj, _ = Delegacion.objects.update_or_create(
                id_delegacion=d['id'],
                defaults={
                    'codigo': d['codigo'],
                    'nombre': d['nombre'],
                    'direccion': d['direccion'],
                    'comuna': d['comuna'],
                    'ambito': d['ambito'],
                    'responsable': d['responsable'],
                    'foco_estrategico': d['foco_estrategico'],
                    'estado': d['estado'],
                }
            )
            delegacion_objs[d['id']] = obj

        self.stdout.write(self.style.SUCCESS(f'Delegaciones procesadas: {len(delegacion_objs)}'))

        # 3. Superusuario y Cuentas de Acceso con Perfiles
        usuarios_data = [
            {
                'username': 'coordinador',
                'email': 'coordinador@correo.cl',
                'first_name': 'Coordinador',
                'last_name': 'Comunal',
                'password': 'admin',
                'is_staff': False,
                'is_superuser': False,
                'rol_codigo': 'ROL-COORD',
                'delegacion_id': 1,
                'delegaciones_ids': [1, 2, 3, 4],
            },
            {
                'username': 'heman',
                'email': 'heman@correo.cl',
                'first_name': 'He-Man',
                'last_name': 'Delegado',
                'password': 'admin',
                'is_staff': False,
                'is_superuser': False,
                'rol_codigo': 'ROL-DEL',
                'delegacion_id': 1,
                'delegaciones_ids': [1],
            },
            {
                'username': 'flash',
                'email': 'flash@correo.cl',
                'first_name': 'Flash',
                'last_name': 'Social',
                'password': 'admin',
                'is_staff': False,
                'is_superuser': False,
                'rol_codigo': 'ROL-GES',
                'delegacion_id': 1,
                'delegaciones_ids': [1],
            },
            {
                'username': 'acuaman',
                'email': 'acuaman@correo.cl',
                'first_name': 'Acuaman',
                'last_name': 'Territorial',
                'password': 'admin',
                'is_staff': False,
                'is_superuser': False,
                'rol_codigo': 'ROL-TER',
                'delegacion_id': 2,
                'delegaciones_ids': [2],
            },
            {
                'username': 'capitanamarvel',
                'email': 'capitanamarvel@correo.cl',
                'first_name': 'Capitana',
                'last_name': 'Marvel',
                'password': 'admin',
                'is_staff': False,
                'is_superuser': False,
                'rol_codigo': 'ROL-DIS',
                'delegacion_id': 4,
                'delegaciones_ids': [4],
            },
            {
                'username': 'spiderman',
                'email': 'spiderman@correo.cl',
                'first_name': 'Spider',
                'last_name': 'Man',
                'password': 'admin',
                'is_staff': False,
                'is_superuser': False,
                'rol_codigo': 'ROL-TER',
                'delegacion_id': 1,
                'delegaciones_ids': [1],
            },
            {
                'username': 'capitanamerica',
                'email': 'capitanamerica@correo.cl',
                'first_name': 'Capitán',
                'last_name': 'América',
                'password': 'admin',
                'is_staff': False,
                'is_superuser': False,
                'rol_codigo': 'ROL-GES',
                'delegacion_id': 2,
                'delegaciones_ids': [2],
            },
            {
                'username': 'panteranegra',
                'email': 'panteranegra@correo.cl',
                'first_name': 'Pantera',
                'last_name': 'Negra',
                'password': 'admin',
                'is_staff': False,
                'is_superuser': False,
                'rol_codigo': 'ROL-OPE',
                'delegacion_id': 3,
                'delegaciones_ids': [3],
            },
            {
                'username': 'hulk',
                'email': 'hulk@correo.cl',
                'first_name': 'Hulk',
                'last_name': 'Social',
                'password': 'admin',
                'is_staff': False,
                'is_superuser': False,
                'rol_codigo': 'ROL-GES',
                'delegacion_id': 3,
                'delegaciones_ids': [3],
            },
        ]
        for u in usuarios_data:
            user, created = User.objects.get_or_create(username=u['username'])
            user.email = u['email']
            user.first_name = u['first_name']
            user.last_name = u['last_name']
            user.is_staff = u['is_staff']
            user.is_superuser = u['is_superuser']
            user.set_password(u['password'])
            user.save()

            perfil, _ = PerfilUsuario.objects.get_or_create(user=user)
            perfil.rol = roles_objs[u['rol_codigo']]
            perfil.delegacion_activa = delegacion_objs[u['delegacion_id']]
            perfil.estado = 'Activo'
            perfil.save()
            perfil.delegaciones_autorizadas.set([delegacion_objs[did] for did in u['delegaciones_ids']])

        self.stdout.write(self.style.SUCCESS(f'Usuarios y perfiles procesados: {len(usuarios_data)}'))

        # 4. Catálogo de Ítems y Metas (CRUD 4)
        items_data = [
            {
                'codigo': 'I01',
                'nombre': 'Atención de Usuario Presencial y Telefónica',
                'descripcion': 'Recepción, registro y orientación personalizada de vecinos en delegación',
                'tipo_meta': 'Cuantitativa',
            },
            {
                'codigo': 'I02',
                'nombre': 'Informes Sociales y Ficha FIBE',
                'descripcion': 'Levantamiento de peritajes sociales y aplicación de ficha básica de emergencia',
                'tipo_meta': 'Cuantitativa',
            },
            {
                'codigo': 'I03',
                'nombre': 'Gestión Territorial y Operativos en Terreno',
                'descripcion': 'Visitas a juntas de vecinos, supervisión de microbasurales y espacios públicos',
                'tipo_meta': 'Cuantitativa',
            },
            {
                'codigo': 'I04',
                'nombre': 'Emergencias Comunales y Contingencias',
                'descripcion': 'Respuesta rápida ante emergencias climáticas, cortes de servicios o siniestros',
                'tipo_meta': 'Cuantitativa',
            },
            {
                'codigo': 'I05',
                'nombre': 'Capacitación y Participación Ciudadana',
                'descripcion': 'Talleres comunitarios, mesas de trabajo barriales y difusión municipal',
                'tipo_meta': 'Cualitativa',
            },
        ]

        item_objs = {}
        for item in items_data:
            obj, _ = ItemMeta.objects.update_or_create(
                codigo=item['codigo'],
                defaults={
                    'nombre': item['nombre'],
                    'descripcion': item['descripcion'],
                    'tipo_meta': item['tipo_meta'],
                    'estado': 'Activo',
                }
            )
            item_objs[item['codigo']] = obj
        self.stdout.write(self.style.SUCCESS(f'Ítems de metas procesados: {len(item_objs)}'))

        # 5. Catálogo de Tipo y Sub Atención (CRUD 5 y 6)
        tipos_atencion_data = [
            {
                'codigo': 'TIP-SOC',
                'nombre': 'Atención Social y Beneficios',
                'descripcion': 'Asistencia económica, subsidios familiares y ayudas técnicas inmediatas',
                'subatenciones': [
                    ('SUB-ORI', 'Orientación Social y Registro Social de Hogares'),
                    ('SUB-FIBE', 'Aplicación de Ficha FIBE'),
                    ('SUB-SUBS', 'Postulación a Subsidios de Agua y Vivienda'),
                    ('SUB-ALIM', 'Entrega de Cajas de Alimentos y Albergue'),
                ]
            },
            {
                'codigo': 'TIP-TERR',
                'nombre': 'Gestión Territorial y Obras',
                'descripcion': 'Requerimientos de luminarias, bacheo, aseo y plazas vecinales',
                'subatenciones': [
                    ('SUB-LUM', 'Reparación de Luminarias y Alumbrado Público'),
                    ('SUB-ASEO', 'Operativo de Tolvas y Retiro de Escombros'),
                    ('SUB-PLAZ', 'Mantención y Riego de Áreas Verdes / Plazas'),
                    ('SUB-BACH', 'Bacheo y Señalización Vial'),
                ]
            },
            {
                'codigo': 'TIP-SEG',
                'nombre': 'Seguridad Ciudadana e Inspección',
                'descripcion': 'Denuncias vecinales, patrullaje preventivo y mediación comunitaria',
                'subatenciones': [
                    ('SUB-PATR', 'Solicitud de Patrullaje Preventivo'),
                    ('SUB-RUID', 'Mediación Vecinal por Ruidos Molestos'),
                    ('SUB-COME', 'Fiscalización de Comercio Informal'),
                ]
            },
        ]

        tipo_objs = {}
        subatencion_objs = {}
        for tip in tipos_atencion_data:
            tipo_obj, _ = TipoAtencion.objects.update_or_create(
                codigo=tip['codigo'],
                defaults={
                    'nombre': tip['nombre'],
                    'descripcion': tip['descripcion'],
                    'estado': 'Activo',
                }
            )
            tipo_objs[tip['codigo']] = tipo_obj

            for sub_cod, sub_nom in tip['subatenciones']:
                sub_obj, _ = SubAtencion.objects.update_or_create(
                    codigo=sub_cod,
                    defaults={
                        'id_tipo': tipo_obj,
                        'nombre': sub_nom,
                        'estado': 'Activo',
                    }
                )
                subatencion_objs[sub_cod] = sub_obj

        self.stdout.write(self.style.SUCCESS(f'Tipos de atención ({len(tipo_objs)}) y Subatenciones ({len(subatencion_objs)}) procesados.'))


        # 3. Funcionarios
        funcionarios_data = [
            {'id': 1, 'delegacion_id': 1, 'nombre': 'He-Man', 'cargo': 'Delegado Municipal', 'activo': True, 'fecha_ingreso': datetime.date(2024, 1, 1), 'username': 'heman'},
            {'id': 2, 'delegacion_id': 2, 'nombre': 'Acuaman', 'cargo': 'Territorial OO.CC. 1', 'activo': True, 'fecha_ingreso': datetime.date(2024, 3, 15), 'username': 'acuaman'},
            {'id': 3, 'delegacion_id': 1, 'nombre': 'Flash', 'cargo': 'Gestor Social 1', 'activo': True, 'fecha_ingreso': datetime.date(2024, 2, 1), 'username': 'flash'},
            {'id': 4, 'delegacion_id': 3, 'nombre': 'Pantera Negra', 'cargo': 'Prof. Planificación y Control', 'activo': True, 'fecha_ingreso': datetime.date(2024, 1, 10), 'username': 'panteranegra'},
            {'id': 5, 'delegacion_id': 4, 'nombre': 'Capitana Marvel', 'cargo': 'Coordinador DISERCO', 'activo': True, 'fecha_ingreso': datetime.date(2024, 4, 1), 'username': 'capitanamarvel'},
            {'id': 6, 'delegacion_id': 3, 'nombre': 'Hulk', 'cargo': 'Gestor Social 3', 'activo': True, 'fecha_ingreso': datetime.date(2024, 2, 15), 'username': 'hulk'},
            {'id': 7, 'delegacion_id': 2, 'nombre': 'Capitán América', 'cargo': 'Gestor Social 2', 'activo': True, 'fecha_ingreso': datetime.date(2024, 3, 1), 'username': 'capitanamerica'},
            {'id': 8, 'delegacion_id': 1, 'nombre': 'Spider-Man', 'cargo': 'Territorial OO.CC. 2', 'activo': True, 'fecha_ingreso': datetime.date(2024, 5, 10), 'username': 'spiderman'},
        ]

        funcionario_objs = {}
        for f in funcionarios_data:
            user_f = User.objects.filter(username=f['username']).first()
            obj, created = Funcionario.objects.update_or_create(
                id_funcionario=f['id'],
                defaults={
                    'id_delegacion': delegacion_objs[f['delegacion_id']],
                    'nombre': f['nombre'],
                    'cargo': f['cargo'],
                    'activo': f['activo'],
                    'fecha_ingreso': f['fecha_ingreso'],
                    'user': user_f,
                }
            )
            funcionario_objs[f['id']] = obj
        
