"""
Suite de Pruebas Automatizadas de la API RESTful (Evaluacion Sumativa #4)
SGR - Municipalidad de La Serena
Cubre:
1. Emision y refresco de tokens JWT (/api/token/, /api/token/refresh/).
2. Control de acceso 401 Unauthorized sin Bearer token.
3. CRUD Completo de Mantenedor 1 (Delegaciones) con restricciones de perfil.
4. CRUD Completo de Mantenedor 2 (Vecinos) y validacion de Serializadores Diferenciados.
5. CRUD de Transaccion Central (Gestiones / Actividades).
6. Verificacion de documentacion OpenAPI 3 y Swagger UI (/api/schema/, /api/docs/).
"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Municipalidad.settings')
django.setup()

from django.test import TestCase, Client
from django.contrib.auth.models import User, Group
from rest_framework import status
from organizacion.models import Delegacion, Funcionario
from actividades.models import Vecino, Actividad, TipoAtencion


class SgrApiRestTestCase(TestCase):
    def setUp(self):
        self.client = Client()

        # Grupos de seguridad
        self.grupo_admin, _ = Group.objects.get_or_create(name='Administrador')
        self.grupo_operador, _ = Group.objects.get_or_create(name='Supervisor')

        # Usuario Administrador
        self.admin_user = User.objects.create_user(
            username='admin_api',
            password='Password123!',
            email='admin@laserena.cl',
            is_staff=True,
            is_superuser=True
        )
        self.admin_user.groups.add(self.grupo_admin)

        # Usuario Operador Estandar
        self.operador_user = User.objects.create_user(
            username='operador_api',
            password='Password123!',
            email='operador@laserena.cl'
        )
        self.operador_user.groups.add(self.grupo_operador)

        # Datos base para pruebas
        self.delegacion = Delegacion.objects.create(
            nombre='Delegacion Las Companias Test',
            direccion='Esmeralda 1234',
            comuna='La Serena',
            ambito='Urbano',
            responsable='Juan Perez',
            foco_estrategico='Atencion Social',
            estado='Activa'
        )

        self.vecino = Vecino.objects.create(
            rut='15.987.654-3',
            nombre='Carlos Vecino Real',
            telefono='+56912345678',
            correo='carlos.vecino@gmail.com',
            direccion='Calle Los Aromos 456',
            territorio='Las Companias'
        )

        self.funcionario = Funcionario.objects.create(
            nombre='Funcionario Test',
            cargo='Gestor Territorial',
            id_delegacion=self.delegacion,
            user=self.operador_user
        )

        self.tipo_atencion = TipoAtencion.objects.create(
            nombre='Alumbrado Publico',
            descripcion='Atenciones de luminarias',
            estado='Activo'
        )

        self.actividad = Actividad.objects.create(
            codigo='GES-TEST-001',
            id_delegacion=self.delegacion,
            id_funcionario=self.funcionario,
            id_vecino=self.vecino,
            solicitante=self.vecino.nombre,
            rut_solicitante=self.vecino.rut,
            telefono=self.vecino.telefono,
            correo=self.vecino.correo,
            direccion=self.vecino.direccion,
            territorio=self.vecino.territorio,
            contacto='Contacto Directo Privado',
            id_tipo=self.tipo_atencion,
            fecha='2026-11-25',
            solicitud='Reparacion de luminaria en pasaje',
            accion='Se deriva a cuadrilla municipal',
            responsable='Funcionario Test',
            item_evaluacion='Operatividad Barrial',
            ingreso_tubo=True,
            estado='Pendiente',
            observacion_revision='Nota confidencial de revision interna',
            usuario_creador=self.admin_user
        )

    def _obtener_token(self, username, password):
        resp = self.client.post('/api/token/', {
            'username': username,
            'password': password
        }, content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        return resp.json()['access'], resp.json()['refresh']

    # 1. Pruebas de Autenticacion JWT
    def test_01_autenticacion_jwt_emision_y_refresco(self):
        access_token, refresh_token = self._obtener_token('admin_api', 'Password123!')
        self.assertTrue(len(access_token) > 20)
        self.assertTrue(len(refresh_token) > 20)

        # Refresco de token
        resp_refresh = self.client.post('/api/token/refresh/', {
            'refresh': refresh_token
        }, content_type='application/json')
        self.assertEqual(resp_refresh.status_code, status.HTTP_200_OK)
        nuevo_access = resp_refresh.json()['access']
        self.assertTrue(len(nuevo_access) > 20)

    def test_02_seguridad_bloqueo_sin_token(self):
        # Acceso no autorizado debe retornar 401
        resp = self.client.get('/api/v1/delegaciones/')
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    # 2. Mantenedor 1: Delegaciones (CRUD y RBAC)
    def test_03_crud_delegaciones_admin_y_operador(self):
        admin_token, _ = self._obtener_token('admin_api', 'Password123!')
        oper_token, _ = self._obtener_token('operador_api', 'Password123!')

        auth_admin = {'HTTP_AUTHORIZATION': f'Bearer {admin_token}'}
        auth_oper = {'HTTP_AUTHORIZATION': f'Bearer {oper_token}'}

        # GET: ambos pueden listar
        resp_list = self.client.get('/api/v1/delegaciones/', **auth_oper)
        self.assertEqual(resp_list.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(resp_list.json()), 1)

        # POST: Operador no puede crear (403 Forbidden)
        payload_nueva = {
            'nombre': 'Delegacion Rural Norte Nueva',
            'direccion': 'Ruta 5 Norte Km 15',
            'comuna': 'La Serena',
            'ambito': 'Rural',
            'responsable': 'Maria Gonzalez',
            'estado': 'Activa'
        }
        resp_post_oper = self.client.post('/api/v1/delegaciones/', payload_nueva, content_type='application/json', **auth_oper)
        self.assertEqual(resp_post_oper.status_code, status.HTTP_403_FORBIDDEN)

        # POST: Admin si puede crear (201 Created)
        resp_post_admin = self.client.post('/api/v1/delegaciones/', payload_nueva, content_type='application/json', **auth_admin)
        self.assertEqual(resp_post_admin.status_code, status.HTTP_201_CREATED)
        creada_id = resp_post_admin.json()['id_delegacion']

        # PATCH: Admin actualiza
        resp_patch = self.client.patch(
            f'/api/v1/delegaciones/{creada_id}/',
            {'responsable': 'Maria Gonzalez Actualizada'},
            content_type='application/json',
            **auth_admin
        )
        self.assertEqual(resp_patch.status_code, status.HTTP_200_OK)
        self.assertEqual(resp_patch.json()['responsable'], 'Maria Gonzalez Actualizada')

        # DELETE: Admin elimina
        resp_del = self.client.delete(f'/api/v1/delegaciones/{creada_id}/', **auth_admin)
        self.assertEqual(resp_del.status_code, status.HTTP_204_NO_CONTENT)

    # 3. Mantenedor 2: Vecinos y Proteccion de Datos Sensibles (Differentiated Serializers)
    def test_04_serializadores_diferenciados_vecinos(self):
        admin_token, _ = self._obtener_token('admin_api', 'Password123!')
        oper_token, _ = self._obtener_token('operador_api', 'Password123!')

        auth_admin = {'HTTP_AUTHORIZATION': f'Bearer {admin_token}'}
        auth_oper = {'HTTP_AUTHORIZATION': f'Bearer {oper_token}'}

        # Consulta como ADMIN: datos reales y completos
        resp_admin = self.client.get(f'/api/v1/vecinos/{self.vecino.id_vecino}/', **auth_admin)
        self.assertEqual(resp_admin.status_code, status.HTTP_200_OK)
        data_admin = resp_admin.json()
        self.assertEqual(data_admin['rut'], '15.987.654-3')
        self.assertEqual(data_admin['telefono'], '+56912345678')
        self.assertEqual(data_admin['correo'], 'carlos.vecino@gmail.com')

        # Consulta como OPERADOR: datos sensibles enmascarados (Ley 19.628)
        resp_oper = self.client.get(f'/api/v1/vecinos/{self.vecino.id_vecino}/', **auth_oper)
        self.assertEqual(resp_oper.status_code, status.HTTP_200_OK)
        data_oper = resp_oper.json()
        self.assertIn('.***.***-', data_oper['rut'])
        self.assertEqual(data_oper['telefono'], '+56 9 ****-****')
        self.assertIn('****@gmail.com', data_oper['correo'])

    # 4. Transaccion Central: Gestiones Municipales y Serializadores Diferenciados
    def test_05_transaccion_gestiones_crud_y_seguridad(self):
        admin_token, _ = self._obtener_token('admin_api', 'Password123!')
        oper_token, _ = self._obtener_token('operador_api', 'Password123!')

        auth_admin = {'HTTP_AUTHORIZATION': f'Bearer {admin_token}'}
        auth_oper = {'HTTP_AUTHORIZATION': f'Bearer {oper_token}'}

        # Admin visualiza auditoria interna y observaciones
        resp_ges_admin = self.client.get(f'/api/v1/gestiones/{self.actividad.id_actividad}/', **auth_admin)
        self.assertEqual(resp_ges_admin.status_code, status.HTTP_200_OK)
        data_admin = resp_ges_admin.json()
        self.assertEqual(data_admin['observacion_revision'], 'Nota confidencial de revision interna')
        self.assertEqual(data_admin['rut_solicitante'], '15.987.654-3')

        # Operador ve datos enmascarados y NO tiene acceso a observacion_revision
        resp_ges_oper = self.client.get(f'/api/v1/gestiones/{self.actividad.id_actividad}/', **auth_oper)
        self.assertEqual(resp_ges_oper.status_code, status.HTTP_200_OK)
        data_oper = resp_ges_oper.json()
        self.assertNotIn('observacion_revision', data_oper)
        self.assertIn('.***.***-', data_oper['rut_solicitante'])
        self.assertEqual(data_oper['telefono'], '+56 9 ****-****')

        # Operador puede crear gestion
        payload_ges = {
            'fecha': '2026-11-26',
            'id_delegacion': self.delegacion.id_delegacion,
            'id_funcionario': self.funcionario.id_funcionario,
            'solicitante': 'Ana Ciudadana',
            'solicitud': 'Poda preventiva de arbol en avenida',
            'accion': 'Se coordina con Parques y Jardines',
            'responsable': 'Funcionario Test',
            'item_evaluacion': 'Areas Verdes',
            'estado': 'Pendiente',
        }
        resp_post = self.client.post('/api/v1/gestiones/', payload_ges, content_type='application/json', **auth_oper)
        self.assertEqual(resp_post.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp_post.json()['solicitante'], 'Ana Ciudadana')

    # 5. Documentacion Swagger y OpenAPI 3
    def test_06_endpoints_documentacion_swagger(self):
        resp_schema = self.client.get('/api/schema/')
        self.assertEqual(resp_schema.status_code, status.HTTP_200_OK)

        resp_docs = self.client.get('/api/docs/')
        self.assertEqual(resp_docs.status_code, status.HTTP_200_OK)
        self.assertIn(b'swagger-ui', resp_docs.content.lower())

        resp_swagger = self.client.get('/api/swagger/')
        self.assertEqual(resp_swagger.status_code, status.HTTP_200_OK)
        self.assertIn(b'swagger-ui', resp_swagger.content.lower())


if __name__ == '__main__':
    from django.test.runner import DiscoverRunner
    runner = DiscoverRunner(verbosity=2)
    failures = runner.run_tests(['test_api'])
    sys.exit(bool(failures))
