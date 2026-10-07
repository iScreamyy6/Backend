import datetime
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from organizacion.models import Delegacion, Funcionario
from actividades.models import Actividad, Evidencia
from agenda.models import Compromiso
from resultados.models import PeriodoEvaluacion, MetaFuncionario, IndicadorDelegacion


class Command(BaseCommand):
    help = 'Pobla la base de datos con información inicial del SGR (Ilustre Municipalidad de La Serena)'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.NOTICE('Iniciando poblamiento de datos...'))

        # 1. Superusuario para Django Admin
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@laserena.cl', 'admin123')
            self.stdout.write(self.style.SUCCESS('Superusuario creado: admin / admin123'))
        else:
            self.stdout.write(self.style.WARNING('Superusuario "admin" ya existe.'))

        # 2. Delegaciones
        delegaciones_data = [
            {
                'id': 1,
                'nombre': 'Delegación Municipal Las Compañías',
                'ambito': 'Las Compañías Alta y Baja',
                'responsable': 'He-Man',
                'foco_estrategico': 'Atención integral comunitaria, operativos sociales y resolución territorial rápida',
                'estado': 'Activa'
            },
            {
                'id': 2,
                'nombre': 'Delegación Municipal La Antena',
                'ambito': 'Sector La Antena y Florida',
                'responsable': 'Thor',
                'foco_estrategico': 'Seguridad vecinal, recuperación de espacios públicos y mediación comunitaria',
                'estado': 'Activa'
            },
            {
                'id': 3,
                'nombre': 'Delegación Municipal Centro y Casco Histórico',
                'ambito': 'Centro Urbano y Casco Histórico',
                'responsable': 'Batman',
                'foco_estrategico': 'Fiscalización comercial, turismo patrimonial y aseo urbano',
                'estado': 'Activa'
            },
            {
                'id': 4,
                'nombre': 'Delegación Municipal Rural',
                'ambito': 'Valles y Localidades Rurales',
                'responsable': 'Superman',
                'foco_estrategico': 'Conectividad hídrica, caminos rurales y apoyo a crianceros',
                'estado': 'Activa'
            },
        ]

        delegacion_objs = {}
        for d in delegaciones_data:
            obj, created = Delegacion.objects.update_or_create(
                id=d['id'],
                defaults={
                    'nombre': d['nombre'],
                    'ambito': d['ambito'],
                    'responsable': d['responsable'],
                    'foco_estrategico': d['foco_estrategico'],
                    'estado': d['estado'],
                }
            )
            delegacion_objs[d['id']] = obj

        self.stdout.write(self.style.SUCCESS(f'Delegaciones procesadas: {len(delegacion_objs)}'))

        # 3. Funcionarios
        funcionarios_data = [
            {'id': 1, 'delegacion_id': 1, 'nombre': 'He-Man', 'cargo': 'Delegado Municipal', 'activo': True, 'fecha_ingreso': datetime.date(2024, 1, 1)},
            {'id': 2, 'delegacion_id': 1, 'nombre': 'Acuaman', 'cargo': 'Territorial OO.CC. 1', 'activo': True, 'fecha_ingreso': datetime.date(2024, 3, 15)},
            {'id': 3, 'delegacion_id': 1, 'nombre': 'Flash', 'cargo': 'Gestor Social 1', 'activo': True, 'fecha_ingreso': datetime.date(2024, 2, 1)},
            {'id': 4, 'delegacion_id': 1, 'nombre': 'Pantera Negra', 'cargo': 'Prof. Planificación y Control', 'activo': True, 'fecha_ingreso': datetime.date(2024, 1, 10)},
            {'id': 5, 'delegacion_id': 1, 'nombre': 'Capitana Marvel', 'cargo': 'Coordinador DISERCO', 'activo': True, 'fecha_ingreso': datetime.date(2024, 4, 1)},
            {'id': 6, 'delegacion_id': 1, 'nombre': 'Hulk', 'cargo': 'Gestor Social 3', 'activo': True, 'fecha_ingreso': datetime.date(2024, 2, 15)},
            {'id': 7, 'delegacion_id': 1, 'nombre': 'Capitán América', 'cargo': 'Gestor Social 2', 'activo': True, 'fecha_ingreso': datetime.date(2024, 3, 1)},
            {'id': 8, 'delegacion_id': 1, 'nombre': 'Spider-Man', 'cargo': 'Territorial OO.CC. 2', 'activo': True, 'fecha_ingreso': datetime.date(2024, 5, 10)},
        ]

        funcionario_objs = {}
        for f in funcionarios_data:
            obj, created = Funcionario.objects.update_or_create(
                id=f['id'],
                defaults={
                    'delegacion': delegacion_objs[f['delegacion_id']],
                    'nombre': f['nombre'],
                    'cargo': f['cargo'],
                    'activo': f['activo'],
                    'fecha_ingreso': f['fecha_ingreso'],
                }
            )
            funcionario_objs[f['id']] = obj

        self.stdout.write(self.style.SUCCESS(f'Funcionarios procesados: {len(funcionario_objs)}'))

        # 4. Período de Evaluación
        periodo, created = PeriodoEvaluacion.objects.update_or_create(
            id=1,
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
                'fecha': datetime.date(2026, 7, 6),
                'solicitud': 'Solicitud de Reunión por vehículos mal estacionados',
                'accion': 'Gestionar Reunión con vecinos y directiva',
                'responsable': 'Acuaman',
                'item_evaluacion': 'ATENCION DE USUARIO TELEFONO Y PRESENCIAL',
                'estado': 'Realizado',
                'contacto': 'María González',
                'telefono': '+56 9 8765 4321',
                'ingreso_tubo': False,
                'codigo_evidencia': 'EVI-2026-0901',
            },
            {
                'id': 2,
                'fecha': datetime.date(2026, 7, 6),
                'solicitud': 'Solicitud de Poda en Sector de Uruguay con Pasaje Totoral',
                'accion': 'Gestionar Poda e inspección de cuadrilla',
                'responsable': 'Acuaman',
                'item_evaluacion': 'ATENCION DE USUARIO TELEFONO Y PRESENCIAL',
                'estado': 'Realizado',
                'contacto': 'Carlos Muñoz',
                'telefono': '+56 9 5544 3322',
                'ingreso_tubo': True,
                'codigo_evidencia': 'EVI-2026-0902',
            },
            {
                'id': 3,
                'fecha': datetime.date(2026, 7, 1),
                'solicitud': 'Entrega de documentación para aporte económico por incendio',
                'accion': 'Visita Terreno y Entrega de Informe Social',
                'responsable': 'Flash',
                'item_evaluacion': 'INFORMES SOCIALES',
                'estado': 'Realizado',
                'contacto': 'Rosa Valenzuela',
                'telefono': '+56 9 9988 7766',
                'ingreso_tubo': False,
                'codigo_evidencia': 'EVI-2026-0903',
            },
            {
                'id': 4,
                'fecha': datetime.date(2026, 7, 8),
                'solicitud': 'Coordinación Gestión territorial actividad navidad',
                'accion': 'Reunión logística con juntas vecinales',
                'responsable': 'Pantera Negra',
                'item_evaluacion': 'EMERGENCIA',
                'estado': 'Realizado',
                'contacto': 'Pedro Soto',
                'telefono': '+56 9 3322 1100',
                'ingreso_tubo': False,
                'codigo_evidencia': 'EVI-2026-0904',
            },
        ]

        actividad_objs = {}
        for a in actividades_data:
            obj, created = Actividad.objects.update_or_create(
                id=a['id'],
                defaults={
                    'fecha': a['fecha'],
                    'solicitud': a['solicitud'],
                    'accion': a['accion'],
                    'responsable': a['responsable'],
                    'item_evaluacion': a['item_evaluacion'],
                    'estado': a['estado'],
                    'contacto': a['contacto'],
                    'telefono': a['telefono'],
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
                id=e['id'],
                defaults={
                    'actividad': actividad_objs[e['actividad_id']],
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
                'fecha_compromiso': datetime.date(2026, 9, 15),
                'area_apoyo': 'Parques y Jardines',
                'observaciones': 'Cuadrilla programada para semana entrante',
                'estado': 'EN PROCESO',
                'unidad': 1,
            },
            {
                'id': 4,
                'fecha_solicitud': datetime.date(2026, 7, 6),
                'actividad': 'Salida a terreno y catastro con dirigentes',
                'tipo': 'EXT',
                'solicitante': 'Delegación',
                'territorio': 'Sector La Campiña',
                'responsable': 'Hulk',
                'fecha_compromiso': datetime.date(2026, 9, 25),
                'area_apoyo': 'Obras Municipales',
                'observaciones': 'A la espera de confirmación de vehículo municipal',
                'estado': 'PENDIENTE',
                'unidad': 1,
            },
        ]

        for c in compromisos_data:
            Compromiso.objects.update_or_create(
                id=c['id'],
                defaults={
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
                    'unidad': c['unidad'],
                }
            )

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
                id=m['id'],
                defaults={
                    'funcionario': funcionario_objs[m['funcionario_id']],
                    'periodo': periodo,
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
                id=ind['id'],
                defaults={
                    'delegacion': delegacion_objs[ind['delegacion_id']],
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
        self.stdout.write(self.style.SUCCESS('¡Poblamiento completado exitosamente!'))
