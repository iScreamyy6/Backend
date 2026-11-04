from django.shortcuts import render, redirect
from django.utils import timezone
from django.db.models import Count, Q
from django.contrib.auth.models import User

from actividades.models import Actividad
from agenda.models import Compromiso
from organizacion.models import Delegacion, Funcionario


def inicio(request):
    if not request.user.is_authenticated:
        return redirect('login')

    user = request.user
    perfil = getattr(user, 'perfil', None)
    rol_codigo = perfil.rol.codigo if (perfil and perfil.rol) else ('ROL-ADM' if user.is_superuser else 'ROL-OPE')
    rol_nombre = perfil.rol.nombre if (perfil and perfil.rol) else ('Administrador General' if user.is_superuser else 'Funcionario Municipal')

    # Determinar Perfil Oficial de Acceso (Eva #3: Administrador, Supervisor, Administrativo)
    if user.is_superuser or user.groups.filter(name='Administrador').exists() or rol_codigo == 'ROL-ADM':
        perfil_tier = 'Administrador'
    elif user.groups.filter(name='Supervisor').exists() or rol_codigo in ('ROL-COORD', 'ROL-DEL', 'ROL-VERIF'):
        perfil_tier = 'Supervisor'
    else:
        perfil_tier = 'Administrativo'

    hoy = timezone.now().date()
    inicio_mes = hoy.replace(day=1)

    # Delegación activa
    delegacion_activa_id = request.session.get('delegacion_activa_id')
    delegacion_activa = None
    if delegacion_activa_id:
        delegacion_activa = Delegacion.objects.filter(pk=delegacion_activa_id, estado='Activa').first()
    if not delegacion_activa and perfil and perfil.delegacion_activa:
        delegacion_activa = perfil.delegacion_activa
    if not delegacion_activa:
        delegacion_activa = Delegacion.objects.filter(estado='Activa').first()

    contexto = {
        'rol_codigo': rol_codigo,
        'rol_nombre': rol_nombre,
        'perfil_tier': perfil_tier,
        'perfil_tier_nombre': perfil_tier,
        'delegacion_activa': delegacion_activa,
        'hoy': hoy,
    }

    if perfil_tier == 'Administrador':
        # --- 1. DASHBOARD ADMINISTRADOR (RESUMEN GLOBAL COMUNAL DE GESTIONES) ---
        total_gestiones = Actividad.objects.count()
        gestiones_mes = Actividad.objects.filter(fecha__gte=inicio_mes).count()
        gestiones_resueltas = Actividad.objects.filter(estado__in=['Realizado', 'Cerrado']).count()
        gestiones_proceso = Actividad.objects.filter(estado__in=['En Proceso', 'Pendiente']).count()
        tasa_resolucion_gestiones = round((gestiones_resueltas / total_gestiones * 100) if total_gestiones > 0 else 0, 1)

        # Gestiones Sociales y en Terreno
        total_sociales = Actividad.objects.filter(es_gestion_social=True).count()
        total_derivadas_tubo = Actividad.objects.filter(ingreso_tubo=True).count()

        # Tubo de Trabajo Intersectorial
        total_tubo = Compromiso.objects.count()
        tubo_atrasados = Compromiso.objects.filter(fecha_compromiso__lt=hoy).exclude(estado='REALIZADO').count()
        tubo_proceso = Compromiso.objects.filter(estado='EN PROCESO').exclude(fecha_compromiso__lt=hoy).count()
        tubo_pendientes = Compromiso.objects.filter(estado='PENDIENTE').exclude(fecha_compromiso__lt=hoy).count()
        tubo_ingresados = Compromiso.objects.filter(estado='INGRESADO').exclude(fecha_compromiso__lt=hoy).count()
        tubo_resueltos = Compromiso.objects.filter(estado='REALIZADO').count()
        tasa_resolucion_tubo = round((tubo_resueltos / total_tubo * 100) if total_tubo > 0 else 0, 1)

        total_usuarios = User.objects.count()
        total_delegaciones = Delegacion.objects.filter(estado='Activa').count()
        total_funcionarios = Funcionario.objects.filter(activo=True).count()

        # Distribución de Gestiones por Delegación
        delegaciones_resumen = []
        for d in Delegacion.objects.filter(estado='Activa').annotate(num_ges=Count('actividades_delegacion')):
            pct = round((d.num_ges / total_gestiones * 100) if total_gestiones > 0 else 0, 1)
            num_tubo = Compromiso.objects.filter(id_delegacion=d).count()
            delegaciones_resumen.append({
                'delegacion': d,
                'total_ges': d.num_ges,
                'num_tubo': num_tubo,
                'pct': pct,
            })

        # Últimas gestiones registradas comunales
        ultimas_gestiones = Actividad.objects.select_related('id_delegacion', 'id_tipo', 'id_funcionario').order_by('-fecha_registro')[:8]

        contexto.update({
            'total_gestiones': total_gestiones,
            'gestiones_mes': gestiones_mes,
            'gestiones_resueltas': gestiones_resueltas,
            'gestiones_proceso': gestiones_proceso,
            'tasa_resolucion_gestiones': tasa_resolucion_gestiones,
            'total_sociales': total_sociales,
            'total_derivadas_tubo': total_derivadas_tubo,
            'total_tubo': total_tubo,
            'tubo_atrasados': tubo_atrasados,
            'tubo_proceso': tubo_proceso,
            'tubo_pendientes': tubo_pendientes,
            'tubo_ingresados': tubo_ingresados,
            'tubo_resueltos': tubo_resueltos,
            'tasa_resolucion_tubo': tasa_resolucion_tubo,
            'total_usuarios': total_usuarios,
            'total_delegaciones': total_delegaciones,
            'total_funcionarios': total_funcionarios,
            'delegaciones_resumen': delegaciones_resumen,
            'ultimas_gestiones': ultimas_gestiones,
        })

    elif perfil_tier == 'Supervisor':
        # --- 2. DASHBOARD SUPERVISOR (RESUMEN TERRITORIAL DE GESTIONES) ---
        q_del = Q(id_delegacion=delegacion_activa) if delegacion_activa else Q()

        total_gestiones_del = Actividad.objects.filter(q_del).count()
        gestiones_mes_del = Actividad.objects.filter(q_del, fecha__gte=inicio_mes).count()
        gestiones_resueltas_del = Actividad.objects.filter(q_del, estado__in=['Realizado', 'Cerrado']).count()
        gestiones_proceso_del = Actividad.objects.filter(q_del, estado__in=['En Proceso', 'Pendiente']).count()
        tasa_resolucion_del = round((gestiones_resueltas_del / total_gestiones_del * 100) if total_gestiones_del > 0 else 0, 1)

        sociales_del = Actividad.objects.filter(q_del, es_gestion_social=True).count()

        total_tubo_del = Compromiso.objects.filter(q_del).count()
        tubo_del_atrasados = Compromiso.objects.filter(q_del, fecha_compromiso__lt=hoy).exclude(estado='REALIZADO').count()
        tubo_del_proceso = Compromiso.objects.filter(q_del, estado='EN PROCESO').exclude(fecha_compromiso__lt=hoy).count()
        tubo_del_pendientes = Compromiso.objects.filter(q_del, estado__in=['PENDIENTE', 'INGRESADO']).exclude(fecha_compromiso__lt=hoy).count()
        tubo_del_resueltos = Compromiso.objects.filter(q_del, estado='REALIZADO').count()
        tasa_resolucion_tubo_del = round((tubo_del_resueltos / total_tubo_del * 100) if total_tubo_del > 0 else 0, 1)

        # Compromisos urgentes o atrasados del sector
        compromisos_urgentes = Compromiso.objects.filter(q_del, fecha_compromiso__lt=hoy).exclude(estado='REALIZADO').order_by('fecha_compromiso')[:6]

        # Funcionarios en la delegación
        funcionarios_del = Funcionario.objects.filter(id_delegacion=delegacion_activa, activo=True) if delegacion_activa else []

        # Últimas gestiones de la delegación
        ultimas_gestiones_del = Actividad.objects.filter(q_del).select_related('id_tipo', 'id_funcionario').order_by('-fecha_registro')[:8]

        contexto.update({
            'total_gestiones_del': total_gestiones_del,
            'gestiones_mes_del': gestiones_mes_del,
            'gestiones_resueltas_del': gestiones_resueltas_del,
            'gestiones_proceso_del': gestiones_proceso_del,
            'tasa_resolucion_del': tasa_resolucion_del,
            'sociales_del': sociales_del,
            'total_tubo_del': total_tubo_del,
            'tubo_del_atrasados': tubo_del_atrasados,
            'tubo_del_proceso': tubo_del_proceso,
            'tubo_del_pendientes': tubo_del_pendientes,
            'tubo_del_resueltos': tubo_del_resueltos,
            'tasa_resolucion_tubo_del': tasa_resolucion_tubo_del,
            'compromisos_urgentes': compromisos_urgentes,
            'funcionarios_del': funcionarios_del,
            'ultimas_gestiones_del': ultimas_gestiones_del,
        })

    else:
        # --- 3. DASHBOARD ADMINISTRATIVO (RESUMEN OPERATIVO PERSONAL DE GESTIONES) ---
        q_user_ges = Q(usuario_creador=user) | Q(responsable__icontains=user.username)
        if user.first_name:
            q_user_ges |= Q(responsable__icontains=user.first_name)

        q_user_tubo = Q(usuario_creador=user) | Q(responsable__icontains=user.username)
        if user.first_name:
            q_user_tubo |= Q(responsable__icontains=user.first_name)

        mis_gestiones_total = Actividad.objects.filter(q_user_ges).count()
        mis_gestiones_mes = Actividad.objects.filter(q_user_ges, fecha__gte=inicio_mes).count()
        mis_gestiones_resueltas = Actividad.objects.filter(q_user_ges, estado__in=['Realizado', 'Cerrado']).count()
        mis_gestiones_proceso = Actividad.objects.filter(q_user_ges, estado__in=['En Proceso', 'Pendiente']).count()

        mis_tubo_total = Compromiso.objects.filter(q_user_tubo).count()
        mis_tubo_atrasados = Compromiso.objects.filter(q_user_tubo, fecha_compromiso__lt=hoy).exclude(estado='REALIZADO').count()
        mis_tubo_proceso = Compromiso.objects.filter(q_user_tubo, estado='EN PROCESO').exclude(fecha_compromiso__lt=hoy).count()
        mis_tubo_resueltos = Compromiso.objects.filter(q_user_tubo, estado='REALIZADO').count()

        # Tareas / Compromisos prioritarios activos del funcionario
        mis_compromisos_activos = Compromiso.objects.filter(q_user_tubo).exclude(estado='REALIZADO').order_by('fecha_compromiso')[:6]

        # Últimas gestiones registradas por este funcionario
        mis_ultimas_gestiones = Actividad.objects.filter(q_user_ges).select_related('id_tipo').order_by('-fecha_registro')[:6]

        # Fichas sociales si aplica
        social_fichas = 0
        social_visitas_pendientes = 0
        if rol_codigo == 'ROL-GES':
            social_fichas = Actividad.objects.filter(q_user_ges, es_gestion_social=True).count()
            social_visitas_pendientes = Actividad.objects.filter(q_user_ges, es_gestion_social=True, requiere_visita=True, fecha_visita__isnull=True).count()

        contexto.update({
            'mis_gestiones_total': mis_gestiones_total,
            'mis_gestiones_mes': mis_gestiones_mes,
            'mis_gestiones_resueltas': mis_gestiones_resueltas,
            'mis_gestiones_proceso': mis_gestiones_proceso,
            'mis_tubo_total': mis_tubo_total,
            'mis_tubo_atrasados': mis_tubo_atrasados,
            'mis_tubo_proceso': mis_tubo_proceso,
            'mis_tubo_resueltos': mis_tubo_resueltos,
            'mis_compromisos_activos': mis_compromisos_activos,
            'mis_ultimas_gestiones': mis_ultimas_gestiones,
            'social_fichas': social_fichas,
            'social_visitas_pendientes': social_visitas_pendientes,
        })

    return render(request, 'inicio.html', contexto)
