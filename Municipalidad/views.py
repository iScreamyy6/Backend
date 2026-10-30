from django.shortcuts import render, redirect

def inicio(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    perfil = getattr(request.user, 'perfil', None)
    rol_codigo = perfil.rol.codigo if (perfil and perfil.rol) else ('ROL-ADM' if request.user.is_superuser else 'ROL-OPE')
    rol_nombre = perfil.rol.nombre if (perfil and perfil.rol) else ('Administrador General' if request.user.is_superuser else 'Funcionario Municipal')

    # Determinar Perfil Oficial de Acceso (Eva #3: Administrador, Supervisor, Administrativo)
    if request.user.is_superuser or request.user.groups.filter(name='Administrador').exists() or rol_codigo == 'ROL-ADM':
        perfil_tier = 'Administrador'
    elif request.user.groups.filter(name='Supervisor').exists() or rol_codigo in ('ROL-COORD', 'ROL-DEL', 'ROL-VERIF'):
        perfil_tier = 'Supervisor'
    else:
        perfil_tier = 'Administrativo'

    return render(request, 'inicio.html', {
        'rol_codigo': rol_codigo,
        'rol_nombre': rol_nombre,
        'perfil_tier': perfil_tier,
    })
