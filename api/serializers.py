import re
from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from organizacion.models import Delegacion
from actividades.models import Vecino, Actividad, TipoAtencion, SubAtencion


def mask_rut(rut_str):
    if not rut_str:
        return 'Sin RUT'
    clean = str(rut_str).strip()
    if len(clean) >= 4:
        return clean[:3] + '.***.***-' + clean[-1]
    return '***-X'


def mask_phone(phone_str):
    if not phone_str:
        return 'No registrado'
    return '+56 9 ****-****'


def mask_email(email_str):
    if not email_str:
        return 'No registrado'
    parts = email_str.split('@')
    if len(parts) == 2:
        user_part, domain = parts
        masked_user = user_part[0] + '****' if len(user_part) > 1 else '****'
        return f"{masked_user}@{domain}"
    return 'c*****@***.***'


# ==============================================================================
# MANTENEDOR 1: DELEGACIONES MUNICIPALES
# ==============================================================================
class DelegacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Delegacion
        fields = [
            'id_delegacion',
            'codigo',
            'nombre',
            'direccion',
            'comuna',
            'ambito',
            'responsable',
            'foco_estrategico',
            'estado',
            'fecha_creacion',
        ]
        read_only_fields = ['id_delegacion', 'codigo', 'fecha_creacion']


# ==============================================================================
# MANTENEDOR 2: VECINOS Y PADRON CIUDADANO (SERIALIZADORES DIFERENCIADOS)
# ==============================================================================
class VecinoAdminSerializer(serializers.ModelSerializer):
    """
    Perfil Administrador: Acceso total e irrestricto a los datos personales,
    contacto, correo y direccion real de los vecinos.
    """
    class Meta:
        model = Vecino
        fields = [
            'id_vecino',
            'rut',
            'nombre',
            'telefono',
            'correo',
            'direccion',
            'territorio',
            'fecha_registro',
        ]
        read_only_fields = ['id_vecino', 'fecha_registro']


class VecinoPublicSerializer(serializers.ModelSerializer):
    """
    Perfil Operador / Estandar: Enmascara campos sensibles de identidad y contacto
    (RUT, Telefono, Correo) en conformidad a la Ley 19.628 de Proteccion de Datos.
    """
    rut = serializers.SerializerMethodField()
    telefono = serializers.SerializerMethodField()
    correo = serializers.SerializerMethodField()

    class Meta:
        model = Vecino
        fields = [
            'id_vecino',
            'rut',
            'nombre',
            'telefono',
            'correo',
            'direccion',
            'territorio',
            'fecha_registro',
        ]
        read_only_fields = ['id_vecino', 'fecha_registro']

    @extend_schema_field(serializers.CharField())
    def get_rut(self, obj):
        return mask_rut(obj.rut)

    @extend_schema_field(serializers.CharField())
    def get_telefono(self, obj):
        return mask_phone(obj.telefono)

    @extend_schema_field(serializers.CharField())
    def get_correo(self, obj):
        return mask_email(obj.correo)


# ==============================================================================
# TRANSACCION DEL NEGOCIO: GESTIONES Y ACTIVIDADES TERRITORIALES
# ==============================================================================
class ActividadAdminSerializer(serializers.ModelSerializer):
    """
    Perfil Administrador: Auditoria completa, datos de contacto sin censura,
    revisor interno, notas de observacion de evidencia y enlaces a Tubo de Trabajo.
    """
    delegacion_nombre = serializers.ReadOnlyField(source='id_delegacion.nombre')
    funcionario_nombre = serializers.ReadOnlyField(source='id_funcionario.nombre')
    tipo_nombre = serializers.ReadOnlyField(source='id_tipo.nombre')

    class Meta:
        model = Actividad
        fields = [
            'id_actividad',
            'codigo',
            'fecha',
            'id_delegacion',
            'delegacion_nombre',
            'id_funcionario',
            'funcionario_nombre',
            'id_vecino',
            'solicitante',
            'rut_solicitante',
            'telefono',
            'correo',
            'direccion',
            'territorio',
            'contacto',
            'id_tipo',
            'tipo_nombre',
            'solicitud',
            'accion',
            'responsable',
            'item_evaluacion',
            'ingreso_tubo',
            'id_compromiso',
            'fecha_limite_tubo',
            'area_apoyo_tubo',
            'estado',
            'codigo_evidencia',
            'estado_evidencia',
            'tipo_impacto',
            'observacion_revision',
            'fecha_revision',
            'usuario_creador',
            'usuario_revisor',
        ]
        read_only_fields = ['id_actividad', 'codigo', 'codigo_evidencia', 'fecha_revision']


class ActividadUserSerializer(serializers.ModelSerializer):
    """
    Perfil Operador / Estandar: Protege datos personales del vecino solicitante
    (RUT, Telefono, Correo enmascarados) y excluye notas privadas de auditoria interna.
    """
    delegacion_nombre = serializers.ReadOnlyField(source='id_delegacion.nombre')
    funcionario_nombre = serializers.ReadOnlyField(source='id_funcionario.nombre')
    tipo_nombre = serializers.ReadOnlyField(source='id_tipo.nombre')
    rut_solicitante = serializers.SerializerMethodField()
    telefono = serializers.SerializerMethodField()
    correo = serializers.SerializerMethodField()
    contacto = serializers.SerializerMethodField()

    class Meta:
        model = Actividad
        fields = [
            'id_actividad',
            'codigo',
            'fecha',
            'id_delegacion',
            'delegacion_nombre',
            'id_funcionario',
            'funcionario_nombre',
            'id_vecino',
            'solicitante',
            'rut_solicitante',
            'telefono',
            'correo',
            'direccion',
            'territorio',
            'contacto',
            'id_tipo',
            'tipo_nombre',
            'solicitud',
            'accion',
            'responsable',
            'item_evaluacion',
            'ingreso_tubo',
            'estado',
            'estado_evidencia',
            'tipo_impacto',
        ]
        read_only_fields = ['id_actividad', 'codigo']

    @extend_schema_field(serializers.CharField())
    def get_rut_solicitante(self, obj):
        return mask_rut(obj.rut_solicitante)

    @extend_schema_field(serializers.CharField())
    def get_telefono(self, obj):
        return mask_phone(obj.telefono)

    @extend_schema_field(serializers.CharField())
    def get_correo(self, obj):
        return mask_email(obj.correo)

    @extend_schema_field(serializers.CharField())
    def get_contacto(self, obj):
        return '[PROTEGIDO - LEY 19.628]' if obj.contacto else 'Sin contacto'
