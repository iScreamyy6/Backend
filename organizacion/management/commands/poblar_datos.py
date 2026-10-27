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
                'username': 'admin',
                'email': 'admin@laserena.cl',
                'first_name': 'Administrador',
                'last_name': 'General',
                'password': 'admin',
                'is_staff': True,
                'is_superuser': True,
                'rol_codigo': 'ROL-ADM',
                'delegacion_id': 1,
                'delegaciones_ids': [1, 2, 3, 4],
            },
            {
                'username': 'coordinador',
                'email': 'coordinador@laserena.cl',
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
                'username': 'delegado_d01',
                'email': 'delegado_d01@laserena.cl',
                'first_name': 'Delegado',
                'last_name': 'Las Compañías',
                'password': 'admin',
                'is_staff': False,
                'is_superuser': False,
                'rol_codigo': 'ROL-DEL',
                'delegacion_id': 1,
                'delegaciones_ids': [1],
            },
            {
                'username': 'operador_d01',
                'email': 'operador_d01@laserena.cl',
                'first_name': 'Operador',
                'last_name': 'Social D01',
                'password': 'admin',
                'is_staff': False,
                'is_superuser': False,
                'rol_codigo': 'ROL-OPE',
                'delegacion_id': 1,
                'delegaciones_ids': [1],
            },
            {
                'username': 'operador_d02',
                'email': 'operador_d02@laserena.cl',
                'first_name': 'Operador',
                'last_name': 'Territorial D02',
                'password': 'admin',
                'is_staff': False,
                'is_superuser': False,
                'rol_codigo': 'ROL-OPE',
                'delegacion_id': 2,
                'delegaciones_ids': [2],
            },
            {
                'username': 'diserco',
                'email': 'diserco@laserena.cl',
                'first_name': 'Funcionario',
                'last_name': 'DISERCO',
                'password': 'admin',
                'is_staff': False,
                'is_superuser': False,
                'rol_codigo': 'ROL-OPE',
                'delegacion_id': 1,
                'delegaciones_ids': [1],
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
        user_delegado = User.objects.filter(username='delegado_d01').first()
        user_operador1 = User.objects.filter(username='operador_d01').first()
        user_operador2 = User.objects.filter(username='operador_d02').first()
        user_diserco = User.objects.filter(username='diserco').first()

        funcionarios_data = [
            {'id': 1, 'delegacion_id': 1, 'nombre': 'He-Man', 'cargo': 'Delegado Municipal', 'activo': True, 'fecha_ingreso': datetime.date(2024, 1, 1), 'user': user_delegado},
            {'id': 2, 'delegacion_id': 1, 'nombre': 'Acuaman', 'cargo': 'Territorial OO.CC. 1', 'activo': True, 'fecha_ingreso': datetime.date(2024, 3, 15), 'user': user_operador2},
            {'id': 3, 'delegacion_id': 1, 'nombre': 'Flash', 'cargo': 'Gestor Social 1', 'activo': True, 'fecha_ingreso': datetime.date(2024, 2, 1), 'user': user_operador1},
            {'id': 4, 'delegacion_id': 1, 'nombre': 'Pantera Negra', 'cargo': 'Prof. Planificación y Control', 'activo': True, 'fecha_ingreso': datetime.date(2024, 1, 10), 'user': None},
            {'id': 5, 'delegacion_id': 1, 'nombre': 'Capitana Marvel', 'cargo': 'Coordinador DISERCO', 'activo': True, 'fecha_ingreso': datetime.date(2024, 4, 1), 'user': user_diserco},
            {'id': 6, 'delegacion_id': 1, 'nombre': 'Hulk', 'cargo': 'Gestor Social 3', 'activo': True, 'fecha_ingreso': datetime.date(2024, 2, 15), 'user': None},
            {'id': 7, 'delegacion_id': 1, 'nombre': 'Capitán América', 'cargo': 'Gestor Social 2', 'activo': True, 'fecha_ingreso': datetime.date(2024, 3, 1), 'user': None},
            {'id': 8, 'delegacion_id': 1, 'nombre': 'Spider-Man', 'cargo': 'Territorial OO.CC. 2', 'activo': True, 'fecha_ingreso': datetime.date(2024, 5, 10), 'user': None},
        ]

        funcionario_objs = {}
        for f in funcionarios_data:
            obj, created = Funcionario.objects.update_or_create(
                id_funcionario=f['id'],
                defaults={
                    'id_delegacion': delegacion_objs[f['delegacion_id']],
                    'nombre': f['nombre'],
                    'cargo': f['cargo'],
                    'activo': f['activo'],
                    'fecha_ingreso': f['fecha_ingreso'],
                    'user': f.get('user'),
                }
            )
            funcionario_objs[f['id']] = obj

        self.stdout.write(self.style.SUCCESS(f'Funcionarios procesados: {len(funcionario_objs)}'))

        # Mapeos de Cargo -> Tipo de Gestión (CargoTipoGestion)
        cargos_mapeo_data = [
            # Coordinador DISERCO / Funcionario DISERCO: Obras, Territorial, Seguridad
            ('Coordinador DISERCO', 'TIP-TERR'),
            ('Coordinador DISERCO', 'TIP-SEG'),
            ('DISERCO', 'TIP-TERR'),
            ('DISERCO', 'TIP-SEG'),
            # Gestores Sociales: Atención Social y Beneficios
            ('Gestor Social 1', 'TIP-SOC'),
            ('Gestor Social 2', 'TIP-SOC'),
            ('Gestor Social 3', 'TIP-SOC'),
            ('Gestor Social', 'TIP-SOC'),
            # Territoriales: Gestión Territorial y Obras
            ('Territorial OO.CC. 1', 'TIP-TERR'),
            ('Territorial OO.CC. 2', 'TIP-TERR'),
            ('Territorial OO.CC.', 'TIP-TERR'),
            # Delegado y Planificación: Acceso a todos los tipos
            ('Delegado Municipal', 'TIP-SOC'),
            ('Delegado Municipal', 'TIP-TERR'),
            ('Delegado Municipal', 'TIP-SEG'),
            ('Prof. Planificación y Control', 'TIP-SOC'),
            ('Prof. Planificación y Control', 'TIP-TERR'),
            ('Prof. Planificación y Control', 'TIP-SEG'),
        ]

        cargos_creados = 0
        for cargo_nom, tip_cod in cargos_mapeo_data:
            tip_obj = tipo_objs.get(tip_cod)
            if tip_obj:
                CargoTipoGestion.objects.get_or_create(
                    cargo=cargo_nom,
                    id_tipo=tip_obj
                )
                cargos_creados += 1
        self.stdout.write(self.style.SUCCESS(f'Mapeos Cargo -> Tipo de Gestión procesados: {cargos_creados}'))

        # Vecinos / Solicitantes iniciales
        vecinos_data = [
            {
                'rut': '14.238.901-2',
                'nombre': 'María Elena González Silva',
                'telefono': '+56 9 8765 4321',
                'correo': 'maria.gonzalez@example.test',
                'direccion': 'Pasaje Los Lirios #450, Las Compañías',
                'territorio': 'Las Compañías Alta',
            },
            {
                'rut': '12.876.543-K',
                'nombre': 'Carlos Alberto Tapia Vega',
                'telefono': '+56 9 7654 3210',
                'correo': 'carlos.tapia@example.test',
                'direccion': 'Av. Islón con Lautaro, Las Compañías',
                'territorio': 'Las Compañías Baja',
            },
            {
                'rut': '16.543.210-9',
                'nombre': 'Juana de Lourdes Rojas Pérez',
                'telefono': '+56 9 6543 2109',
                'correo': 'juana.rojas@example.test',
                'direccion': 'Calle 18 de Septiembre #890, La Antena',
                'territorio': 'Sector La Antena',
            },
            {
                'rut': '9.988.776-6',
                'nombre': 'Rosa Valenzuela',
                'telefono': '+56 9 9988 7766',
                'correo': 'rosa.valenzuela@example.test',
                'direccion': 'Pasaje Totoral #120, Las Compañías Alta',
                'territorio': 'Las Compañías Alta',
            },
            {
                'rut': '3.322.110-0',
                'nombre': 'Pedro Soto',
                'telefono': '+56 9 3322 1100',
                'correo': 'pedro.soto@example.test',
                'direccion': 'Av. La Paz #340, La Florida',
                'territorio': 'Sector La Florida',
            },
        ]

        vecino_objs = {}
        for v in vecinos_data:
            v_obj, _ = Vecino.objects.update_or_create(
                rut=v['rut'],
                defaults=v
            )
            vecino_objs[v['rut']] = v_obj
        self.stdout.write(self.style.SUCCESS(f'Vecinos registrados: {len(vecino_objs)}'))

        # 4. Período de Evaluación
        periodo, created = PeriodoEvaluacion.objects.update_or_create(
            id_periodo=1,
            defaults={
                'nombre': '3er Trimestre 2026',
                'fecha_inicio': datetime.date(2026, 7, 1),
                'fecha_cierre': datetime.date(2026, 9, 30),
                'dias_totales': 90,
                'activo': True,
            }
        )
        self.stdout.write(self.style.SUCCESS('Período de evaluación procesado.'))

        # 5. Actividades
        actividades_data = [
            {
                'id': 1,
                'funcionario_id': 2,
                'fecha': datetime.date(2026, 7, 6),
                'solicitud': 'Solicitud de Reunión por vehículos mal estacionados',
                'accion': 'Gestionar Reunión con vecinos y directiva',
                'responsable': 'Acuaman',
                'item_evaluacion': 'ATENCION DE USUARIO TELEFONO Y PRESENCIAL',
                'estado': 'Realizado',
                'contacto': 'María González',
                'telefono': '+56 9 8765 4321',
                'territorio': 'Sector Casco Histórico',
                'ingreso_tubo': False,
                'codigo_evidencia': 'EVI-2026-0901',
            },
            {
                'id': 2,
                'funcionario_id': 2,
                'fecha': datetime.date(2026, 7, 6),
                'solicitud': 'Solicitud de Poda en Sector de Uruguay con Pasaje Totoral',
                'accion': 'Gestionar Poda e inspección de cuadrilla',
                'responsable': 'Acuaman',
                'item_evaluacion': 'ATENCION DE USUARIO TELEFONO Y PRESENCIAL',
                'estado': 'Realizado',
                'contacto': 'Carlos Muñoz',
                'telefono': '+56 9 5544 3322',
                'territorio': 'Sector Uruguay',
                'ingreso_tubo': True,
                'codigo_evidencia': 'EVI-2026-0902',
            },
            {
                'id': 3,
                'funcionario_id': 3,
                'fecha': datetime.date(2026, 7, 1),
                'solicitud': 'Entrega de documentación para aporte económico por incendio',
                'accion': 'Visita Terreno y Entrega de Informe Social',
                'responsable': 'Flash',
                'item_evaluacion': 'INFORMES SOCIALES',
                'estado': 'Realizado',
                'contacto': 'Rosa Valenzuela',
                'telefono': '+56 9 9988 7766',
                'territorio': 'Las Compañías Alta',
                'ingreso_tubo': False,
                'codigo_evidencia': 'EVI-2026-0903',
            },
            {
                'id': 4,
                'funcionario_id': 4,
                'fecha': datetime.date(2026, 7, 8),
                'solicitud': 'Coordinación Gestión territorial actividad navidad',
                'accion': 'Reunión logística con juntas vecinales',
                'responsable': 'Pantera Negra',
                'item_evaluacion': 'EMERGENCIA',
                'estado': 'Realizado',
                'contacto': 'Pedro Soto',
                'telefono': '+56 9 3322 1100',
                'territorio': 'Sector La Florida',
                'ingreso_tubo': False,
                'codigo_evidencia': 'EVI-2026-0904',
            },
        ]

        actividad_objs = {}
        for a in actividades_data:
            obj, created = Actividad.objects.update_or_create(
                id_actividad=a['id'],
                defaults={
                    'id_funcionario': funcionario_objs[a['funcionario_id']],
                    'fecha': a['fecha'],
                    'solicitud': a['solicitud'],
                    'accion': a['accion'],
                    'responsable': a['responsable'],
                    'item_evaluacion': a['item_evaluacion'],
                    'estado': a['estado'],
                    'contacto': a['contacto'],
                    'solicitante': a['contacto'],
                    'telefono': a['telefono'],
                    'territorio': a['territorio'],
                    'ingreso_tubo': a['ingreso_tubo'],
                    'codigo_evidencia': a['codigo_evidencia'],
                }
            )
            actividad_objs[a['id']] = obj

        self.stdout.write(self.style.SUCCESS(f'Actividades procesadas: {len(actividad_objs)}'))

        # 6. Evidencias
        evidencias_data = [
            {
                'id': 1,
                'actividad_id': 1,
                'codigo': 'EVI-2026-0901',
                'imagen_verificada': True,
                'verificador_valido': 1,
                'resultado': 1,
                'estado_validacion': 'Aprobada',
                'observacion': 'Acta firmada con timbre de delegación conforme',
            },
            {
                'id': 2,
                'actividad_id': 2,
                'codigo': 'EVI-2026-0902',
                'imagen_verificada': True,
                'verificador_valido': 1,
                'resultado': 1,
                'estado_validacion': 'Aprobada',
                'observacion': 'Fotografía de poda antes y después verificada',
            },
            {
                'id': 3,
                'actividad_id': 3,
                'codigo': 'EVI-2026-0903',
                'imagen_verificada': False,
                'verificador_valido': 1,
                'resultado': 0,
                'estado_validacion': 'Pendiente',
                'observacion': 'Pendiente visación de jefatura DIDECO',
            },
            {
                'id': 4,
                'actividad_id': 4,
                'codigo': 'EVI-2026-0904',
                'imagen_verificada': False,
                'verificador_valido': 0,
                'resultado': 0,
                'estado_validacion': 'Corregir',
                'observacion': 'Fotografía borrosa requiere reemplazo',
            },
        ]

        for e in evidencias_data:
            Evidencia.objects.update_or_create(
                id_evidencia=e['id'],
                defaults={
                    'id_actividad': actividad_objs[e['actividad_id']],
                    'codigo': e['codigo'],
                    'imagen_verificada': e['imagen_verificada'],
                    'verificador_valido': e['verificador_valido'],
                    'resultado': e['resultado'],
                    'estado_validacion': e['estado_validacion'],
                    'observacion': e['observacion'],
                }
            )

        self.stdout.write(self.style.SUCCESS('Evidencias procesadas.'))

        # 7. Compromisos (Agenda)
        compromisos_data = [
            {
                'id': 1,
                'fecha_solicitud': datetime.date(2026, 7, 6),
                'actividad': 'Boulevard Las Compañías — Coordinación feriantes',
                'tipo': 'EXT',
                'solicitante': 'Delegación',
                'territorio': 'Plaza El Salitre',
                'responsable': 'Spider-Man',
                'funcionario_id': 8,
                'fecha_compromiso': datetime.date(2026, 8, 15),
                'area_apoyo': 'Fomento Productivo',
                'observaciones': 'Operativo instalado y ejecutado',
                'estado': 'REALIZADO',
                'unidad': 1,
            },
            {
                'id': 2,
                'fecha_solicitud': datetime.date(2026, 7, 6),
                'actividad': '1° Encuentro de centros de madre sector Las Violetas',
                'tipo': 'EXT',
                'solicitante': 'Centro de Madres Las Violetas',
                'territorio': 'Sector Las Violetas',
                'responsable': 'Iron Man',
                'funcionario_id': None,
                'fecha_compromiso': datetime.date(2026, 8, 20),
                'area_apoyo': 'DIDECO',
                'observaciones': 'Finalizado con asistencia de 60 dirigentas',
                'estado': 'REALIZADO',
                'unidad': 1,
            },
            {
                'id': 3,
                'fecha_solicitud': datetime.date(2026, 7, 6),
                'actividad': 'Solicitud de Poda JJVV Terrazas del Brillador',
                'tipo': 'EXT',
                'solicitante': 'JJVV Terrazas del Brillador',
                'territorio': 'Terrazas del Brillador',
                'responsable': 'Capitán América',
                'funcionario_id': 7,
                'fecha_compromiso': datetime.date(2026, 9, 15),
                'area_apoyo': 'Parques y Jardines',
                'observaciones': 'Cuadrilla programada para semana entrante',
                'estado': 'EN PROCESO',
                'unidad': 1,
                'actividad_id': 2,
            },
            {
                'id': 4,
                'fecha_solicitud': datetime.date(2026, 7, 6),
                'actividad': 'Salida a terreno y catastro con dirigentes',
                'tipo': 'EXT',
                'solicitante': 'Delegación',
                'territorio': 'Sector La Campiña',
                'responsable': 'Hulk',
                'funcionario_id': 6,
                'fecha_compromiso': datetime.date(2026, 9, 25),
                'area_apoyo': 'Obras Municipales',
                'observaciones': 'A la espera de confirmación de vehículo municipal',
                'estado': 'PENDIENTE',
                'unidad': 1,
            },
        ]

        for c in compromisos_data:
            resp_obj = funcionario_objs[c['funcionario_id']] if c['funcionario_id'] else None
            act_obj = actividad_objs.get(c.get('actividad_id')) if c.get('actividad_id') else None
            comp_obj, _ = Compromiso.objects.update_or_create(
                id_compromiso=c['id'],
                defaults={
                    'id_delegacion': delegacion_objs[c['unidad']],
                    'id_responsable': resp_obj,
                    'id_actividad': act_obj,
                    'fecha_solicitud': c['fecha_solicitud'],
                    'actividad': c['actividad'],
                    'tipo': c['tipo'],
                    'solicitante': c['solicitante'],
                    'territorio': c['territorio'],
                    'responsable': c['responsable'],
                    'fecha_compromiso': c['fecha_compromiso'],
                    'area_apoyo': c['area_apoyo'],
                    'observaciones': c['observaciones'],
                    'estado': c['estado'],
                }
            )
            if act_obj:
                act_obj.id_compromiso = comp_obj
                act_obj.save(update_fields=['id_compromiso'])

        self.stdout.write(self.style.SUCCESS('Compromisos procesados.'))

        # 8. Metas de Funcionario
        metas_data = [
            {'id': 1, 'funcionario_id': 2, 'periodo_id': 1, 'item': 'ATENCIÓN DE USUARIO PRESENCIAL Y TELEFÓNICA', 'ponderador': 25.00, 'meta_periodo': 40, 'avance_actual': 11, 'felicitaciones': 0, 'reclamos': 0},
            {'id': 2, 'funcionario_id': 2, 'periodo_id': 1, 'item': 'INFORMES SOCIALES Y FICHAS FIBE', 'ponderador': 30.00, 'meta_periodo': 20, 'avance_actual': 6, 'felicitaciones': 0, 'reclamos': 0},
            {'id': 3, 'funcionario_id': 2, 'periodo_id': 1, 'item': 'GESTIÓN TERRITORIAL Y OPERATIVOS', 'ponderador': 25.00, 'meta_periodo': 15, 'avance_actual': 4, 'felicitaciones': 0, 'reclamos': 0},
            {'id': 4, 'funcionario_id': 2, 'periodo_id': 1, 'item': 'EMERGENCIAS COMUNALES Y REUNIONES', 'ponderador': 20.00, 'meta_periodo': 10, 'avance_actual': 3, 'felicitaciones': 0, 'reclamos': 0},
            {'id': 5, 'funcionario_id': 6, 'periodo_id': 1, 'item': 'ATENCIÓN SOCIAL A USUARIO PRESENCIAL', 'ponderador': 35.00, 'meta_periodo': 50, 'avance_actual': 75, 'felicitaciones': 2, 'reclamos': 0},
            {'id': 6, 'funcionario_id': 6, 'periodo_id': 1, 'item': 'VISITA A TERRENO Y PERITAJE', 'ponderador': 25.00, 'meta_periodo': 30, 'avance_actual': 45, 'felicitaciones': 1, 'reclamos': 0},
            {'id': 7, 'funcionario_id': 6, 'periodo_id': 1, 'item': 'ENTREGA DE INFORME Y BENEFICIO', 'ponderador': 25.00, 'meta_periodo': 25, 'avance_actual': 38, 'felicitaciones': 0, 'reclamos': 0},
            {'id': 8, 'funcionario_id': 6, 'periodo_id': 1, 'item': 'EMERGENCIA SOCIAL INMEDIATA', 'ponderador': 15.00, 'meta_periodo': 15, 'avance_actual': 22, 'felicitaciones': 0, 'reclamos': 0},
        ]

        for m in metas_data:
            MetaFuncionario.objects.update_or_create(
                id_meta=m['id'],
                defaults={
                    'id_funcionario': funcionario_objs[m['funcionario_id']],
                    'id_periodo': periodo,
                    'item': m['item'],
                    'ponderador': m['ponderador'],
                    'meta_periodo': m['meta_periodo'],
                    'avance_actual': m['avance_actual'],
                    'felicitaciones': m['felicitaciones'],
                    'reclamos': m['reclamos'],
                }
            )

        self.stdout.write(self.style.SUCCESS('Metas de funcionario procesadas.'))

        # 9. Indicadores de Delegación
        indicadores_data = [
            {'id': 1, 'delegacion_id': 1, 'area': 'GESTOR SOCIAL 3', 'responsable': 'Hulk', 'avance_porcentaje': 150.00, 'estado_semaforo': 'verde', 'licencias': 0, 'vacaciones': 0, 'emergencias': 4, 'compensatorios': 0},
            {'id': 2, 'delegacion_id': 1, 'area': 'GESTOR SOCIAL 2', 'responsable': 'Capitán América', 'avance_porcentaje': 92.70, 'estado_semaforo': 'verde', 'licencias': 2, 'vacaciones': 5, 'emergencias': 2, 'compensatorios': 1},
            {'id': 3, 'delegacion_id': 1, 'area': 'PLANIFICACIÓN Y GESTIÓN', 'responsable': 'Pantera Negra', 'avance_porcentaje': 84.80, 'estado_semaforo': 'verde', 'licencias': 0, 'vacaciones': 0, 'emergencias': 1, 'compensatorios': 2},
            {'id': 4, 'delegacion_id': 1, 'area': 'TERRITORIAL OO.CC. 1', 'responsable': 'Acuaman', 'avance_porcentaje': 28.30, 'estado_semaforo': 'rojo', 'licencias': 10, 'vacaciones': 10, 'emergencias': 1, 'compensatorios': 1},
        ]

        for ind in indicadores_data:
            IndicadorDelegacion.objects.update_or_create(
                id_indicador=ind['id'],
                defaults={
                    'id_delegacion': delegacion_objs[ind['delegacion_id']],
                    'id_periodo': periodo,
                    'area': ind['area'],
                    'responsable': ind['responsable'],
                    'avance_porcentaje': ind['avance_porcentaje'],
                    'estado_semaforo': ind['estado_semaforo'],
                    'licencias': ind['licencias'],
                    'vacaciones': ind['vacaciones'],
                    'emergencias': ind['emergencias'],
                    'compensatorios': ind['compensatorios'],
                }
            )


        self.stdout.write(self.style.SUCCESS('Indicadores de delegación procesados.'))

        # 10. Atenciones Ciudadanas (Casos de prueba iniciales)
        user_operador = User.objects.get(username='operador_d01')
        user_admin = User.objects.get(username='admin')

        atenciones_data = [
            {
                'id': 1,
                'folio': 'ATC-00001',
                'solicitante': 'María Elena González Silva',
                'rut_solicitante': '14.238.901-2',
                'telefono': '+56 9 8765 4321',
                'correo': 'maria.gonzalez@example.test',
                'direccion': 'Pasaje Los Lirios #450, Las Compañías',
                'tipo_codigo': 'TIP-SOC',
                'subatencion_codigo': 'SUB-ORI',
                'descripcion': 'Vecina solicita actualización urgente de porcentaje en Registro Social de Hogares por situación de cesantía sobreviniente.',
                'delegacion_id': 1,
                'usuario': user_operador,
                'estado': 'En Tramite',
            },
            {
                'id': 2,
                'folio': 'ATC-00002',
                'solicitante': 'Carlos Alberto Tapia Vega',
                'rut_solicitante': '12.876.543-K',
                'telefono': '+56 9 7654 3210',
                'correo': 'carlos.tapia@example.test',
                'direccion': 'Av. Islón con Lautaro, Las Compañías',
                'tipo_codigo': 'TIP-TERR',
                'subatencion_codigo': 'SUB-LUM',
                'descripcion': 'Poste con luminaria parpadeante frente a jardín infantil Los Traviesos. Genera sensación de inseguridad en horario vespertino.',
                'delegacion_id': 1,
                'usuario': user_operador,
                'estado': 'Ingresada',
            },
            {
                'id': 3,
                'folio': 'ATC-00003',
                'solicitante': 'Juana de Lourdes Rojas Pérez',
                'rut_solicitante': '16.543.210-9',
                'telefono': '+56 9 6543 2109',
                'correo': 'juana.rojas@example.test',
                'direccion': 'Calle 18 de Septiembre #890, La Antena',
                'tipo_codigo': 'TIP-SOC',
                'subatencion_codigo': 'SUB-ALIM',
                'descripcion': 'Adulto mayor viviendo sola requiere caja de alimentos de emergencia y asistencia de trabajadora social.',
                'delegacion_id': 2,
                'usuario': user_admin,
                'estado': 'Resuelta',
            },
        ]

        for at in atenciones_data:
            AtencionCiudadana.objects.update_or_create(
                id_atencion=at['id'],
                defaults={
                    'folio': at['folio'],
                    'solicitante': at['solicitante'],
                    'rut_solicitante': at['rut_solicitante'],
                    'telefono': at['telefono'],
                    'correo': at['correo'],
                    'direccion': at['direccion'],
                    'id_tipo': tipo_objs[at['tipo_codigo']],
                    'id_subatencion': subatencion_objs[at['subatencion_codigo']],
                    'descripcion': at['descripcion'],
                    'id_delegacion': delegacion_objs[at['delegacion_id']],
                    'id_usuario_responsable': at['usuario'],
                    'estado': at['estado'],
                }
            )
        self.stdout.write(self.style.SUCCESS(f'Atenciones ciudadanas procesadas: {len(atenciones_data)}'))
        self.stdout.write(self.style.SUCCESS('¡Poblamiento completado exitosamente!'))

