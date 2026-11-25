from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static
from . import views
from . import views_auth
from . import views_mantenedores
from actividades.views import api_buscar_vecino

urlpatterns = [
    # Panel Django Admin oficial
    path('admin/', admin.site.urls),

    # Wireframe Interactivo (Artefacto para Ingeniería de Software TI2043)
    path('wireframes/', TemplateView.as_view(template_name='wireframes/wireframe_interactivo_sgr.html'), name='wireframes_interactivos'),

    # Página principal
    path('', views.inicio, name='inicio'),

    # Autenticación y Flujo de Recuperación de Contraseña
    path('login/', views_auth.login_view, name='login'),
    path('logout/', views_auth.logout_view, name='logout'),
    path('recuperar/', views_auth.recuperar_solicitar_view, name='recuperar_solicitar'),
    path('recuperar/validar/', views_auth.recuperar_validar_view, name='recuperar_validar'),
    path('recuperar/nueva-clave/', views_auth.recuperar_nueva_clave_view, name='recuperar_nueva_clave'),
    path('recuperar/reset/<str:uidb64>/<str:token>/', views_auth.recuperar_reset_confirm_view, name='recuperar_reset_confirm'),
    path('cambiar-delegacion/<str:delegacion_id>/', views_auth.cambiar_delegacion_view, name='cambiar_delegacion'),

    # Mantenedores (Los 6 CRUDs obligatorios de la Segunda Evaluación)
    # CRUD 1: Delegaciones
    path('mantenedores/delegaciones/', views_mantenedores.delegaciones_lista, name='delegaciones_lista'),
    path('mantenedores/delegaciones/crear/', views_mantenedores.delegaciones_crear, name='delegaciones_crear'),
    path('mantenedores/delegaciones/<int:pk>/editar/', views_mantenedores.delegaciones_editar, name='delegaciones_editar'),
    path('mantenedores/delegaciones/<int:pk>/eliminar/', views_mantenedores.delegaciones_eliminar, name='delegaciones_eliminar'),

    # CRUD 2: Roles
    path('mantenedores/roles/', views_mantenedores.roles_lista, name='roles_lista'),
    path('mantenedores/roles/crear/', views_mantenedores.roles_crear, name='roles_crear'),
    path('mantenedores/roles/<int:pk>/editar/', views_mantenedores.roles_editar, name='roles_editar'),
    path('mantenedores/roles/<int:pk>/eliminar/', views_mantenedores.roles_eliminar, name='roles_eliminar'),

    # CRUD 3: Usuarios
    path('mantenedores/usuarios/', views_mantenedores.usuarios_lista, name='usuarios_lista'),
    path('mantenedores/usuarios/crear/', views_mantenedores.usuarios_crear, name='usuarios_crear'),
    path('mantenedores/usuarios/<int:pk>/editar/', views_mantenedores.usuarios_editar, name='usuarios_editar'),
    path('mantenedores/usuarios/<int:pk>/eliminar/', views_mantenedores.usuarios_eliminar, name='usuarios_eliminar'),

    # CRUD 4: Ítems y Metas
    path('mantenedores/items/', views_mantenedores.items_lista, name='items_lista'),
    path('mantenedores/items/crear/', views_mantenedores.items_crear, name='items_crear'),
    path('mantenedores/items/<int:pk>/editar/', views_mantenedores.items_editar, name='items_editar'),
    path('mantenedores/items/<int:pk>/eliminar/', views_mantenedores.items_eliminar, name='items_eliminar'),

    # CRUD 5: Tipo de Atención
    path('mantenedores/tipos-atencion/', views_mantenedores.tipos_atencion_lista, name='tipos_atencion_lista'),
    path('mantenedores/tipos-atencion/crear/', views_mantenedores.tipos_atencion_crear, name='tipos_atencion_crear'),
    path('mantenedores/tipos-atencion/<int:pk>/editar/', views_mantenedores.tipos_atencion_editar, name='tipos_atencion_editar'),
    path('mantenedores/tipos-atencion/<int:pk>/eliminar/', views_mantenedores.tipos_atencion_eliminar, name='tipos_atencion_eliminar'),

    # CRUD 6: Sub Atención
    path('mantenedores/subatenciones/', views_mantenedores.subatenciones_lista, name='subatenciones_lista'),
    path('mantenedores/subatenciones/crear/', views_mantenedores.subatenciones_crear, name='subatenciones_crear'),
    path('mantenedores/subatenciones/<int:pk>/editar/', views_mantenedores.subatenciones_editar, name='subatenciones_editar'),
    path('mantenedores/subatenciones/<int:pk>/eliminar/', views_mantenedores.subatenciones_eliminar, name='subatenciones_eliminar'),

    # CRUD 7: Vecinos y Padrón Ciudadano
    path('mantenedores/vecinos/', views_mantenedores.vecinos_lista, name='vecinos_lista'),
    path('mantenedores/vecinos/crear/', views_mantenedores.vecinos_crear, name='vecinos_crear'),
    path('mantenedores/vecinos/<int:pk>/editar/', views_mantenedores.vecinos_editar, name='vecinos_editar'),
    path('mantenedores/vecinos/<int:pk>/eliminar/', views_mantenedores.vecinos_eliminar, name='vecinos_eliminar'),

    # CRUD 8: Territorios
    path('mantenedores/territorios/', views_mantenedores.territorios_lista, name='territorios_lista'),
    path('mantenedores/territorios/crear/', views_mantenedores.territorios_crear, name='territorios_crear'),
    path('mantenedores/territorios/<int:pk>/editar/', views_mantenedores.territorios_editar, name='territorios_editar'),
    path('mantenedores/territorios/<int:pk>/eliminar/', views_mantenedores.territorios_eliminar, name='territorios_eliminar'),

    # CRUD 9: Juntas de Vecinos
    path('mantenedores/juntas-vecinos/', views_mantenedores.juntas_vecinos_lista, name='juntas_vecinos_lista'),
    path('mantenedores/juntas-vecinos/crear/', views_mantenedores.juntas_vecinos_crear, name='juntas_vecinos_crear'),
    path('mantenedores/juntas-vecinos/<int:pk>/editar/', views_mantenedores.juntas_vecinos_editar, name='juntas_vecinos_editar'),
    path('mantenedores/juntas-vecinos/<int:pk>/eliminar/', views_mantenedores.juntas_vecinos_eliminar, name='juntas_vecinos_eliminar'),
    path('mantenedores/juntas-vecinos/<int:pk>/detalle/', views_mantenedores.juntas_vecinos_detalle, name='juntas_vecinos_detalle'),
    path('mantenedores/juntas-vecinos/<int:pk>/agregar-dirigente/', views_mantenedores.juntas_vecinos_agregar_dirigente, name='juntas_vecinos_agregar_dirigente'),
    path('mantenedores/participacion/<int:pk_participacion>/quitar/', views_mantenedores.juntas_vecinos_quitar_dirigente, name='juntas_vecinos_quitar_dirigente'),

    # Ingreso y Módulo de Atención Ciudadana
    path('atenciones/', views_mantenedores.atenciones_lista, name='atenciones_lista'),
    path('atenciones/nueva/', views_mantenedores.atencion_nueva, name='atencion_nueva'),
    path('atenciones/<int:pk>/', views_mantenedores.atenciones_detalle, name='atenciones_detalle'),
    # API RESTful Oficial (Evaluacion Sumativa #4 - DRF, JWT, Swagger)
    path('api/', include('api.urls')),

    path('api/subatenciones/', views_mantenedores.api_subatenciones_por_tipo, name='api_subatenciones'),
    path('api/territorios-por-delegacion/', views_mantenedores.api_territorios_por_delegacion, name='api_territorios_por_delegacion'),
    path('api/vecinos/buscar/', api_buscar_vecino, name='api_buscar_vecino'),

    # Módulos preexistentes de Evaluaciones Anteriores
    path('organizacion/', include('organizacion.urls')),
    path('actividades/', include('actividades.urls')),
    path('agenda/', include('agenda.urls')),
    path('resultados/', include('resultados.urls')),
]

from django.urls import re_path
from django.views.static import serve

urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]