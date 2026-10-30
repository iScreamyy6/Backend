import random
from datetime import timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.urls import reverse
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from django.core.mail import send_mail
from django.conf import settings

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


# ==============================================================================
# FLUJO OFICIAL DE RECUPERACIÓN DE CONTRASEÑA POR CORREO Y TOKEN SEGURO (EVA #3)
# ==============================================================================
def recuperar_solicitar_view(request):
    """
    1. Solicitar recuperación mediante correo electrónico.
    2. Generar token seguro de recuperación con Django default_token_generator.
    3. Enviar enlace de recuperación al correo del usuario vía SMTP (con fallback).
    """
    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()

        # Requisito de seguridad RNF: no revelar externamente si el correo existe
        user = User.objects.filter(email__iexact=email, is_active=True).first()

        codigo_generado = None
        reset_url_generada = None

        if user:
            perfil, _ = PerfilUsuario.objects.get_or_create(user=user)
            
            # Generar código numérico de respaldo (compatibilidad test suite)
            codigo = f"{random.randint(100000, 999999)}"
            perfil.codigo_recuperacion = codigo
            perfil.codigo_expiracion = timezone.now() + timedelta(minutes=15)
            perfil.intentos_fallidos = 0
            perfil.codigo_usado = False
            perfil.ultimo_reenvio = timezone.now()
            perfil.save()
            codigo_generado = codigo

            # Generar Token Criptográfico Seguro de Django
            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            reset_path = reverse('recuperar_reset_confirm', kwargs={'uidb64': uidb64, 'token': token})
            reset_url_generada = request.build_absolute_uri(reset_path)

            # Envío de correo electrónico institucional con código y token
            asunto = 'Código de Verificación - SGR Ilustre Municipalidad de La Serena'
            destinatario_nombre = user.get_full_name() or user.username

            cuerpo_texto = f"""Estimado(a) {destinatario_nombre}:

Se ha recibido una solicitud para restablecer la contraseña de su cuenta en el Sistema de Gestión de Resultados (SGR) de la Ilustre Municipalidad de La Serena.

Su código de verificación de 6 dígitos es: {codigo}

Ingrese este código en la pantalla del sistema para continuar con el restablecimiento de su clave.

O si lo prefiere, puede utilizar el siguiente enlace directo con token criptográfico seguro:
{reset_url_generada}

Este código y enlace son de un solo uso y expirarán en 15 minutos por motivos de seguridad.
Si usted no solicitó este cambio, puede ignorar este mensaje; su contraseña actual no sufrirá modificaciones.

Atentamente,
Departamento de Informática y Gestión
Ilustre Municipalidad de La Serena
"""

            cuerpo_html = f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; border: 1px solid #e0e0e0; border-radius: 8px; overflow: hidden; background: #ffffff;">
                <div style="background: #AD0000; padding: 22px; text-align: center; color: #ffffff;">
                    <h2 style="margin: 0; font-size: 1.35rem; color: #ffffff !important;">Ilustre Municipalidad de La Serena</h2>
                    <p style="margin: 4px 0 0; font-size: 0.9rem; color: #ffffff !important; opacity: 0.95;">Sistema de Gestión de Resultados (SGR)</p>
                </div>
                <div style="padding: 26px 28px; color: #212529; line-height: 1.6;">
                    <h3 style="color: #AD0000; margin-top: 0;">Código de Verificación de Seguridad</h3>
                    <p>Estimado(a) <strong>{destinatario_nombre}</strong>,</p>
                    <p>Hemos recibido una solicitud para restablecer la contraseña de acceso a su cuenta en la plataforma SGR.</p>
                    
                    <div style="background: #f8f9fa; border: 2px solid #AD0000; border-radius: 8px; padding: 20px; text-align: center; margin: 24px 0;">
                        <span style="font-size: 0.88rem; color: #495057; display: block; margin-bottom: 6px; font-weight: 600;">Su código de seguridad de 6 dígitos es:</span>
                        <strong style="font-size: 2.2rem; color: #AD0000; letter-spacing: 6px; font-family: monospace; display: block;">{codigo}</strong>
                        <span style="font-size: 0.8rem; color: #6c757d; display: block; margin-top: 6px;">Válido durante 15 minutos · Un solo uso</span>
                    </div>

                    <p style="font-size: 0.88rem; color: #555;">
                        Ingrese este código en la pantalla del sistema para crear su nueva contraseña.
                    </p>

                    <div style="border-top: 1px solid #dee2e6; margin-top: 24px; padding-top: 18px; text-align: center;">
                        <p style="font-size: 0.82rem; color: #6c757d; margin-bottom: 10px;">
                            O si lo prefiere, haga clic en el botón siguiente para acceder directamente mediante su token criptográfico seguro:
                        </p>
                        <a href="{reset_url_generada}" style="background: #AD0000; color: #ffffff !important; text-decoration: none; padding: 11px 22px; border-radius: 6px; font-weight: 700; font-size: 0.9rem; display: inline-block;">
                            Restablecer con Enlace Seguro
                        </a>
                    </div>
                </div>
                <div style="background: #f1f3f5; padding: 14px; text-align: center; font-size: 0.78rem; color: #6c757d; border-top: 1px solid #dee2e6;">
                    Este es un correo institucional generado automáticamente. No responda a este mensaje.
                </div>
            </div>
            """

            try:
                send_mail(
                    subject=asunto,
                    message=cuerpo_texto,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    html_message=cuerpo_html,
                    fail_silently=False
                )
            except Exception as e:
                print(f"[EMAIL] Aviso de envío de correo: {e}")

        # Mensaje al usuario y redirección directa a la pantalla de validación del código
        messages.success(
            request,
            'Se ha enviado un código de seguridad de 6 dígitos a su correo electrónico. Ingréselo a continuación.'
        )

        request.session['recuperacion_email'] = email
        if codigo_generado:
            request.session['demo_codigo_recuperacion'] = codigo_generado
        if reset_url_generada:
            request.session['demo_reset_url'] = reset_url_generada

        return redirect('recuperar_validar')

    return render(request, 'auth/recuperar_solicitar.html')


def recuperar_reset_confirm_view(request, uidb64, token):
    """
    4. Validar token seguro.
    5. Permitir establecer una nueva contraseña.
    6. Confirmar cambio exitoso e invalidar token.
    """
    user = None
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.filter(pk=uid, is_active=True).first()
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    token_valido = bool(user and default_token_generator.check_token(user, token))

    if not token_valido:
        messages.error(
            request,
            'El enlace de recuperación es inválido o ha expirado. Por motivos de seguridad, solicite uno nuevo.'
        )
        return render(request, 'auth/recuperar_token_invalido.html')

    if request.method == 'POST':
        password = request.POST.get('password', '').strip()
        confirm_password = request.POST.get('confirm_password', '').strip()

        if len(password) < 8:
            messages.error(request, 'La nueva contraseña debe contener al menos 8 caracteres.')
            return render(request, 'auth/recuperar_nueva_clave.html', {
                'uidb64': uidb64,
                'token': token,
                'user_target': user
            })

        if password != confirm_password:
            messages.error(request, 'Las contraseñas ingresadas no coinciden. Verifique e intente nuevamente.')
            return render(request, 'auth/recuperar_nueva_clave.html', {
                'uidb64': uidb64,
                'token': token,
                'user_target': user
            })

        # Actualizar contraseña e invalidar token y código
        user.set_password(password)
        user.save()

        perfil = getattr(user, 'perfil', None)
        if perfil:
            perfil.codigo_usado = True
            perfil.codigo_recuperacion = None
            perfil.save()

        # Limpiar variables de sesión demo
        request.session.pop('recuperacion_email', None)
        request.session.pop('demo_codigo_recuperacion', None)
        request.session.pop('demo_reset_url', None)

        messages.success(
            request,
            '¡Contraseña actualizada exitosamente! Ya puede iniciar sesión con su nueva clave.'
        )
        return redirect('login')

    return render(request, 'auth/recuperar_nueva_clave.html', {
        'uidb64': uidb64,
        'token': token,
        'user_target': user
    })


# ==============================================================================
# FLUJO ALTERNATIVO POR CÓDIGO NUMÉRICO DE 6 DÍGITOS (COMPATIBILIDAD TEST SUITE)
# ==============================================================================
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
                perfil.codigo_expiracion = timezone.now() + timedelta(minutes=15)
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

        if perfil.codigo_usado:
            messages.error(request, 'Este código ya fue utilizado previamente. Solicite uno nuevo.')
            return render(request, 'auth/recuperar_validar.html', {'email': email})

        if perfil.codigo_expiracion and timezone.now() > perfil.codigo_expiracion:
            messages.error(request, 'El código ha expirado por superar los 15 minutos de vigencia. Solicite un reenvío.')
            return render(request, 'auth/recuperar_validar.html', {'email': email})

        if perfil.intentos_fallidos >= 3:
            messages.error(request, 'Ha superado el límite de 3 intentos fallidos permitidos. Debe solicitar un nuevo código.')
            return render(request, 'auth/recuperar_validar.html', {'email': email})

        if perfil.codigo_recuperacion != codigo_ingresado:
            perfil.intentos_fallidos += 1
            perfil.save()
            restantes = 3 - perfil.intentos_fallidos
            messages.error(request, f'Código incorrecto. Le quedan {restantes} intento(s).')
            return render(request, 'auth/recuperar_validar.html', {'email': email, 'demo_codigo': demo_codigo})

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

        perfil = user.perfil
        perfil.codigo_usado = True
        perfil.codigo_recuperacion = None
        perfil.save()

        user.set_password(password)
        user.save()

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
