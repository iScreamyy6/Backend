from django.shortcuts import render, redirect

def inicio(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    perfil = getattr(request.user, 'perfil', None)
    rol_codigo = perfil.rol.codigo if (perfil and perfil.rol) else ('ROL-ADM' if request.user.is_superuser else 'ROL-OPE')
    rol_nombre = perfil.rol.nombre if (perfil and perfil.rol) else ('Administrador General' if request.user.is_superuser else 'Funcionario Municipal')

    return render(request, 'inicio.html', {
        'rol_codigo': rol_codigo,
        'rol_nombre': rol_nombre,
    })