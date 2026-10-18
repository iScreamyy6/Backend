import random
from datetime import timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from organizacion.models import Delegacion, PerfilUsuario


def login_view(request):
    if request.user.is_authenticated:
        return redirect('inicio')

    if request.method == 'POST':
        login_input = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()

        if not login_input or not password:
            messages.error(request, 'Debe ingresar su usuario o correo y contraseña.')
            return render(request, 'auth/login.html', {'login_input': login_input})

        # Permitir login por username o por email
        user_candidate = User.objects.filter(Q(username__iexact=login_input) | Q(email__iexact=login_input)).first()
        username = user_candidate.username if user_candidate else login_input

        user = authenticate(request, username=username, password=password)

        if user is not None:
            perfil = getattr(user, 'perfil', None)
            if perfil and perfil.estado == 'Inactivo':
                messages.error(request, 'Esta cuenta de usuario se encuentra inactiva. Comuníquese con la administración.')
                return render(request, 'auth/login.html', {'login_input': login_input})

            login(request, user)

            # Inicializar delegación activa
            if perfil and perfil.delegacion_activa:
                request.session['delegacion_activa_id'] = perfil.delegacion_activa.pk
            elif perfil and perfil.delegaciones_autorizadas.exists():
                request.session['delegacion_activa_id'] = perfil.delegaciones_autorizadas.first().pk
            else:
                primera_del = Delegacion.objects.filter(estado='Activa').first()
                if primera_del:
                    request.session['delegacion_activa_id'] = primera_del.pk

            messages.success(request, f'Bienvenido(a) al Sistema SGR, {user.get_full_name() or user.username}.')
            next_url = request.GET.get('next', 'inicio')
            return redirect(next_url)
        else:
            messages.error(request, 'Credenciales inválidas. Verifique sus datos e intente nuevamente.')

    return render(request, 'auth/login.html')


def logout_view(request):
    logout(request)
    messages.info(request, 'Ha cerrado sesión correctamente.')
    return redirect('login')


def recuperar_solicitar_view(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()

        # Requisito de seguridad RNF: no revelar si el correo existe o no
        user = User.objects.filter(email__iexact=email, is_active=True).first()

        codigo_generado = None
        if user:
            perfil, _ = PerfilUsuario.objects.get_or_create(user=user)
            # Generar código numérico de 6 dígitos
            codigo = f"{random.randint(100000, 999999)}"
            perfil.codigo_recuperacion = codigo
            perfil.codigo_expiracion = timezone.now() + timedelta(minutes=10)
            perfil.intentos_fallidos = 0
            perfil.codigo_usado = False
            perfil.ultimo_reenvio = timezone.now()
            perfil.save()
            codigo_generado = codigo

        # Mensaje genérico de seguridad
        messages.success(
            request,
            'Si el correo electrónico ingresado corresponde a una cuenta registrada en el SGR, '
            'se ha enviado un código de seguridad de 6 dígitos con vigencia de 10 minutos.'
        )

        request.session['recuperacion_email'] = email
        # Guardar en sesión el código con fines académicos de demostración / evaluación local
        if codigo_generado:
            request.session['demo_codigo_recuperacion'] = codigo_generado

        return redirect('recuperar_validar')

    return render(request, 'auth/recuperar_solicitar.html')


def recuperar_validar_view(request):
    email = request.session.get('recuperacion_email', '')
    demo_codigo = request.session.get('demo_codigo_recuperacion', None)

    if request.method == 'POST':
        accion = request.POST.get('accion')

        # Acción: Reenviar código
        if accion == 'reenviar':
            user = User.objects.filter(email__iexact=email, is_active=True).first()
            if user:
                perfil = user.perfil
                if perfil.ultimo_reenvio and (timezone.now() - perfil.ultimo_reenvio).total_seconds() < 45:
                    segundos_restantes = 45 - int((timezone.now() - perfil.ultimo_reenvio).total_seconds())
                    messages.warning(request, f'Debe esperar {segundos_restantes} segundos para solicitar un nuevo código.')
                    return render(request, 'auth/recuperar_validar.html', {'email': email, 'demo_codigo': demo_codigo})

                nuevo_codigo = f"{random.randint(100000, 999999)}"
                perfil.codigo_recuperacion = nuevo_codigo
                perfil.codigo_expiracion = timezone.now() + timedelta(minutes=10)
                perfil.intentos_fallidos = 0
                perfil.codigo_usado = False
                perfil.ultimo_reenvio = timezone.now()
                perfil.save()
                demo_codigo = nuevo_codigo
                request.session['demo_codigo_recuperacion'] = demo_codigo
                messages.success(request, 'Se ha generado y reenviado un nuevo código de 6 dígitos.')
            else:
                messages.success(request, 'Si la cuenta existe, se ha enviado un nuevo código.')
            return render(request, 'auth/recuperar_validar.html', {'email': email, 'demo_codigo': demo_codigo})

        # Acción: Validar código
        # Permite recibir código unido o desde las 6 casillas d1..d6
        c1 = request.POST.get('d1', '')
        c2 = request.POST.get('d2', '')
        c3 = request.POST.get('d3', '')
        c4 = request.POST.get('d4', '')
        c5 = request.POST.get('d5', '')
        c6 = request.POST.get('d6', '')
        codigo_ingresado = (c1 + c2 + c3 + c4 + c5 + c6).strip()
        if not codigo_ingresado:
            codigo_ingresado = request.POST.get('codigo', '').strip()

        if len(codigo_ingresado) != 6 or not codigo_ingresado.isdigit():
            messages.error(request, 'El código debe contener exactamente 6 dígitos numéricos.')
            return render(request, 'auth/recuperar_validar.html', {'email': email, 'demo_codigo': demo_codigo})

        user = User.objects.filter(email__iexact=email, is_active=True).first()

        if not user or not hasattr(user, 'perfil') or not user.perfil.codigo_recuperacion:
            messages.error(request, 'No existe una solicitud de recuperación activa para esta cuenta.')
            return render(request, 'auth/recuperar_validar.html', {'email': email})

        perfil = user.perfil

        # Validar si ya fue usado
        if perfil.codigo_usado:
            messages.error(request, 'Este código ya fue utilizado previamente. Solicite uno nuevo.')
            return render(request, 'auth/recuperar_validar.html', {'email': email})

        # Validar vigencia temporal (10 minutos)
        if perfil.codigo_expiracion and timezone.now() > perfil.codigo_expiracion:
            messages.error(request, 'El código ha expirado por superar los 10 minutos de vigencia. Solicite un reenvío.')
            return render(request, 'auth/recuperar_validar.html', {'email': email})

        # Validar intentos fallidos (máximo 3)
        if perfil.intentos_fallidos >= 3:
            messages.error(request, 'Ha superado el límite de 3 intentos fallidos permitidos. Debe solicitar un nuevo código.')
            return render(request, 'auth/recuperar_validar.html', {'email': email})

        # Validar coincidencia
        if perfil.codigo_recuperacion != codigo_ingresado:
            perfil.intentos_fallidos += 1
            perfil.save()
            restantes = 3 - perfil.intentos_fallidos
            messages.error(request, f'Código incorrecto. Le quedan {restantes} intento(s).')
            return render(request, 'auth/recuperar_validar.html', {'email': email, 'demo_codigo': demo_codigo})

        # Código válido: autorizar paso 3
        request.session['codigo_verificado_user_id'] = user.pk
        messages.success(request, 'Código verificado con éxito. Ingrese su nueva contraseña.')
        return redirect('recuperar_nueva_clave')

    return render(request, 'auth/recuperar_validar.html', {'email': email, 'demo_codigo': demo_codigo})


def recuperar_nueva_clave_view(request):
    user_id = request.session.get('codigo_verificado_user_id')
    if not user_id:
        messages.warning(request, 'Debe validar primero el código de recuperación.')
        return redirect('recuperar_solicitar')

    user = get_object_or_404(User, pk=user_id)

    if request.method == 'POST':
        password = request.POST.get('password', '').strip()
        confirm_password = request.POST.get('confirm_password', '').strip()

        if len(password) < 8:
            messages.error(request, 'La nueva contraseña debe tener al menos 8 caracteres.')
            return render(request, 'auth/recuperar_nueva_clave.html')

        if password != confirm_password:
            messages.error(request, 'Las contraseñas no coinciden. Intente de nuevo.')
            return render(request, 'auth/recuperar_nueva_clave.html')

        # Invalidar código usado y actualizar contraseña
        perfil = user.perfil
        perfil.codigo_usado = True
        perfil.codigo_recuperacion = None
        perfil.save()

        user.set_password(password)
        user.save()

        # Limpiar variables de sesión
        request.session.pop('codigo_verificado_user_id', None)
        request.session.pop('recuperacion_email', None)
        request.session.pop('demo_codigo_recuperacion', None)

        messages.success(request, '¡Contraseña actualizada exitosamente! Ya puede ingresar con su nueva clave.')
        return redirect('login')

    return render(request, 'auth/recuperar_nueva_clave.html')


def cambiar_delegacion_view(request, delegacion_id):
    if not request.user.is_authenticated:
        return redirect('login')

    delegacion = get_object_or_404(Delegacion, pk=delegacion_id, estado='Activa')
    perfil = getattr(request.user, 'perfil', None)

    # Validar permisos en servidor: el perfil debe autorizar esta delegación
    if perfil:
        if perfil.rol and perfil.rol.alcance_autorizado == 'COMUNAL':
            permitido = True
        elif perfil.delegaciones_autorizadas.filter(pk=delegacion.pk).exists():
            permitido = True
        else:
            permitido = False
    else:
        permitido = False

    if permitido:
        request.session['delegacion_activa_id'] = delegacion.pk
        messages.success(request, f'Contexto de trabajo cambiado a: {delegacion.nombre}')
    else:
        messages.error(request, 'No tiene autorización para acceder al contexto de esa delegación.')

    return redirect(request.META.get('HTTP_REFERER', 'inicio'))
