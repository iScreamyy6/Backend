from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Permite lectura a cualquier usuario autenticado,
    pero restringe creacion/edicion/eliminacion exclusivamente a Administradores.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_superuser or request.user.groups.filter(name='Administrador').exists()


class IsAdminUserRole(permissions.BasePermission):
    """
    Exige que el usuario pertenezca al grupo Administrador o sea superusuario.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.is_superuser or request.user.groups.filter(name='Administrador').exists()


class IsStaffOrAuthenticated(permissions.BasePermission):
    """
    Permite acceso completo a usuarios autenticados para operaciones basicas.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)
