from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
    OpenApiParameter,
    OpenApiExample,
    OpenApiResponse,
)
from drf_spectacular.types import OpenApiTypes

from organizacion.models import Delegacion
from actividades.models import Vecino, Actividad
from .permissions import IsAdminOrReadOnly, IsAdminUserRole
from .serializers import (
    DelegacionSerializer,
    VecinoAdminSerializer,
    VecinoPublicSerializer,
    ActividadAdminSerializer,
    ActividadUserSerializer,
)


def es_usuario_admin(user):
    """Comprueba si el usuario autenticado tiene privilegios de Administrador."""
    if not user or not user.is_authenticated:
        return False
    return user.is_superuser or user.groups.filter(name='Administrador').exists()


@extend_schema_view(
    list=extend_schema(summary="Listar todas las delegaciones municipales", tags=["Mantenedor 1: Delegaciones"]),
    retrieve=extend_schema(summary="Obtener detalle de una delegacion municipal", tags=["Mantenedor 1: Delegaciones"]),
    create=extend_schema(
        summary="Crear una nueva delegacion municipal (Solo Administrador)",
        tags=["Mantenedor 1: Delegaciones"],
        examples=[
            OpenApiExample(
                'Ejemplo Creacion Delegacion',
                value={
                    'nombre': 'Delegación Municipal Rural Norte',
                    'direccion': 'Ruta 5 Norte Km 15',
                    'comuna': 'La Serena',
                    'ambito': 'Rural',
                    'responsable': 'Patricia Carmona',
                    'foco_estrategico': 'Conectividad y Fomento Productivo',
                    'estado': 'Activa'
                },
                request_only=True,
            )
        ],
        responses={
            201: DelegacionSerializer,
            400: OpenApiResponse(description="Error de validación en campos"),
            401: OpenApiResponse(description="No autenticado (Falta Bearer token)"),
            403: OpenApiResponse(description="No autorizado (Requiere rol Administrador)")
        }
    ),
    update=extend_schema(summary="Actualizar completamente una delegacion municipal (Solo Administrador)", tags=["Mantenedor 1: Delegaciones"]),
    partial_update=extend_schema(summary="Actualizacion parcial de una delegacion (Solo Administrador)", tags=["Mantenedor 1: Delegaciones"]),
    destroy=extend_schema(summary="Eliminar una delegacion municipal (Solo Administrador)", tags=["Mantenedor 1: Delegaciones"]),
)
class DelegacionViewSet(viewsets.ModelViewSet):
    """
    CRUD RESTful para la entidad Delegacion Municipal (Mantenedor 1).
    Permite lectura a operadores autenticados y mutaciones reservadas a Administrador.
    """
    queryset = Delegacion.objects.all().order_by('id_delegacion')
    serializer_class = DelegacionSerializer
    permission_classes = [IsAdminOrReadOnly]


@extend_schema_view(
    list=extend_schema(
        summary="Listar vecinos del padron comunal",
        description="Aplica serializadores diferenciados: los administradores visualizan RUT, telefonos y correos reales; usuarios operadores reciben datos sensibles enmascarados segun Ley 19.628.",
        tags=["Mantenedor 2: Vecinos / Padron"]
    ),
    retrieve=extend_schema(
        summary="Obtener detalle de un vecino",
        description="Retorna la ficha del vecino. Campos sensibles censurados si el solicitante no es Administrador.",
        tags=["Mantenedor 2: Vecinos / Padron"]
    ),
    create=extend_schema(
        summary="Registrar un nuevo vecino en el padron",
        tags=["Mantenedor 2: Vecinos / Padron"],
        examples=[
            OpenApiExample(
                'Ejemplo Registro Vecino',
                value={
                    'rut': '16.543.210-9',
                    'nombre': 'Elena Morales Silva',
                    'telefono': '+56987654321',
                    'correo': 'elena.morales@gmail.com',
                    'direccion': 'Pasaje Los Pinos 789',
                    'territorio': 'Las Compañías'
                },
                request_only=True,
            )
        ],
        responses={
            201: VecinoAdminSerializer,
            400: OpenApiResponse(description="Error en formato de RUT o datos obligatorios"),
            401: OpenApiResponse(description="No autenticado")
        }
    ),
    update=extend_schema(summary="Actualizar ficha completa del vecino", tags=["Mantenedor 2: Vecinos / Padron"]),
    partial_update=extend_schema(summary="Actualizacion parcial de la ficha del vecino", tags=["Mantenedor 2: Vecinos / Padron"]),
    destroy=extend_schema(summary="Eliminar vecino del padron (Solo Administrador)", tags=["Mantenedor 2: Vecinos / Padron"]),
)
class VecinoViewSet(viewsets.ModelViewSet):
    """
    CRUD RESTful para la entidad Vecino / Padron Ciudadano (Mantenedor 2).
    Implementa proteccion de datos sensibles mediante Serializadores Diferenciados:
    - Administrador: VecinoAdminSerializer (datos completos sin censura).
    - Operador/Estandar: VecinoPublicSerializer (RUT, telefono y correo enmascarados).
    """
    queryset = Vecino.objects.all().order_by('id_vecino')
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if es_usuario_admin(self.request.user):
            return VecinoAdminSerializer
        return VecinoPublicSerializer

    def get_permissions(self):
        # La eliminacion directa de registros ciudadanos esta restringida al perfil Administrador
        if self.action == 'destroy':
            return [IsAdminUserRole()]
        return [permissions.IsAuthenticated()]


@extend_schema_view(
    list=extend_schema(
        summary="Listar gestiones y actividades territoriales (Transaccion Central)",
        description="Listado de gestiones del SGR. Para Administradores expone auditoria y revision interna completa. Para operadores enmascara informacion sensible del vecino solicitante.",
        tags=["Transaccion: Gestiones Municipales"]
    ),
    retrieve=extend_schema(
        summary="Obtener detalle de una gestion municipal",
        tags=["Transaccion: Gestiones Municipales"]
    ),
    create=extend_schema(
        summary="Registrar una nueva gestion municipal",
        tags=["Transaccion: Gestiones Municipales"],
        examples=[
            OpenApiExample(
                'Ejemplo Registro Gestion',
                value={
                    'fecha': '2026-11-25',
                    'id_delegacion': 1,
                    'id_funcionario': 1,
                    'solicitante': 'Elena Morales Silva',
                    'rut_solicitante': '16.543.210-9',
                    'telefono': '+56987654321',
                    'correo': 'elena.morales@gmail.com',
                    'direccion': 'Pasaje Los Pinos 789',
                    'territorio': 'Las Compañías',
                    'contacto': 'Presidenta JJVV Los Pinos',
                    'id_tipo': 1,
                    'solicitud': 'Reparación urgente de matriz de agua potable en vereda',
                    'accion': 'Coordinado en terreno con cuadrilla municipal y empresa sanitaria',
                    'responsable': 'Patricia Carmona',
                    'item_evaluacion': 'Operatividad Barrial',
                    'ingreso_tubo': True,
                    'area_apoyo_tubo': 'Operaciones y Emergencias',
                    'estado': 'Pendiente',
                    'tipo_impacto': 'Cuantitativa'
                },
                request_only=True,
            )
        ],
        responses={
            201: ActividadAdminSerializer,
            400: OpenApiResponse(description="Datos incompletos o inválidos"),
            401: OpenApiResponse(description="No autenticado")
        }
    ),
    update=extend_schema(
        summary="Actualizar completamente una gestion municipal",
        tags=["Transaccion: Gestiones Municipales"]
    ),
    partial_update=extend_schema(
        summary="Actualizacion parcial de una gestion municipal",
        tags=["Transaccion: Gestiones Municipales"]
    ),
    destroy=extend_schema(
        summary="Eliminar una gestion municipal (Solo Administrador)",
        tags=["Transaccion: Gestiones Municipales"]
    ),
)
class ActividadViewSet(viewsets.ModelViewSet):
    """
    CRUD RESTful para la Transaccion Central del Negocio: Actividades / Gestiones.
    Controla el ciclo de atencion, derivacion a Tubo de Trabajo y verificacion de evidencia.
    Aplica Serializadores Diferenciados entre perfil Administrador y Operador.
    """
    queryset = Actividad.objects.all().select_related(
        'id_delegacion', 'id_funcionario', 'id_tipo', 'id_vecino'
    ).order_by('-id_actividad')
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if es_usuario_admin(self.request.user):
            return ActividadAdminSerializer
        return ActividadUserSerializer

    def get_permissions(self):
        if self.action == 'destroy':
            return [IsAdminUserRole()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        user = self.request.user if self.request.user.is_authenticated else None
        serializer.save(usuario_creador=user)
