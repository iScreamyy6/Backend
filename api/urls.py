from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from .views import (
    DelegacionViewSet,
    VecinoViewSet,
    ActividadViewSet,
)

router = DefaultRouter()
router.register(r'delegaciones', DelegacionViewSet, basename='delegacion')
router.register(r'vecinos', VecinoViewSet, basename='vecino')
router.register(r'gestiones', ActividadViewSet, basename='actividad')

urlpatterns = [
    # Autenticacion JWT (JSON Web Tokens)
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Documentacion Interactiva OpenAPI / Swagger / ReDoc
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger_ui'),
    path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    # Endpoints RESTful CRUD
    path('v1/', include(router.urls)),
]
