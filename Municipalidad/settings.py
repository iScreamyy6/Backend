import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# Cargar variables de entorno desde .env
load_dotenv(BASE_DIR / '.env')

SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-default-key-for-dev')

DEBUG = os.getenv('DEBUG', 'True').lower() in ('true', '1', 'yes')

ALLOWED_HOSTS = [host.strip() for host in os.getenv('ALLOWED_HOSTS', '*').split(',') if host.strip()]
if 'testserver' not in ALLOWED_HOSTS and '*' not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append('testserver')


INSTALLED_APPS = [
    'whitenoise.runserver_nostatic',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt',
    'drf_spectacular',
    'agenda',
    'actividades',
    'organizacion',
    'resultados',
    'api',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'Municipalidad.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'Municipalidad.context_processors.delegacion_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'Municipalidad.wsgi.application'

# Configuración dinámica de Base de Datos (SQLite o MySQL)
DB_ENGINE = os.getenv('DB_ENGINE', 'sqlite').lower()

if 'mysql' in DB_ENGINE:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': os.getenv('DB_NAME', 'sgr_municipalidad'),
            'USER': os.getenv('DB_USER', 'root'),
            'PASSWORD': os.getenv('DB_PASSWORD', ''),
            'HOST': os.getenv('DB_HOST', '127.0.0.1'),
            'PORT': os.getenv('DB_PORT', '3306'),
            'OPTIONS': {
                'charset': 'utf8mb4',
                'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            },
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }



AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


LANGUAGE_CODE = 'es'

TIME_ZONE = 'America/Santiago'

USE_I18N = True

USE_TZ = True


STATIC_URL = 'static/'

STATIC_ROOT = BASE_DIR / 'staticfiles'

STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Media files (imágenes de evidencia subidas por los usuarios)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Configuración de Correo Electrónico (Recuperación de Contraseña)
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')

if EMAIL_HOST_USER and EMAIL_HOST_PASSWORD:
    EMAIL_BACKEND = os.getenv('EMAIL_BACKEND', 'django.core.mail.backends.smtp.EmailBackend')
    EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
    EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
    EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True').lower() in ('true', '1', 't')
else:
    EMAIL_BACKEND = os.getenv('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')
    EMAIL_HOST = 'localhost'
    EMAIL_PORT = 25
    EMAIL_USE_TLS = False

DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'SGR La Serena <no-reply@laserena.cl>')
SERVER_EMAIL = DEFAULT_FROM_EMAIL

# Configuracion Django REST Framework (DRF)
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# Configuracion SimpleJWT (Autenticacion mediante Tokens)
from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': False,
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# Configuracion drf-spectacular (OpenAPI 3 / Swagger UI)
SPECTACULAR_SETTINGS = {
    'TITLE': 'SGR Municipalidad de La Serena - API RESTful',
    'DESCRIPTION': (
        'API RESTful del Sistema de Gestion de Resultados (SGR) para la Municipalidad de La Serena.\n\n'
        'Desarrollada para la Evaluacion Sumativa #4 (Programacion Back End TI3V41 - INACAP).\n\n'
        'Caracteristicas Principales:\n'
        '- Autenticacion robusta con JSON Web Tokens (JWT) via Bearer token.\n'
        '- Operaciones CRUD RESTful completas (GET, POST, PUT, DELETE).\n'
        '- Mantenedor 1: Delegaciones Municipales.\n'
        '- Mantenedor 2: Vecinos y Padron Comunal.\n'
        '- Transaccion Central del Negocio: Actividades y Gestiones Territoriales.\n'
        '- Proteccion de Datos Sensibles (Ley 19.628): Serializadores Diferenciados entre Administradores y Operadores.'
    ),
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
    'SECURITY': [{'BearerAuth': []}],
    'APPEND_COMPONENTS': {
        'securitySchemes': {
            'BearerAuth': {
                'type': 'http',
                'scheme': 'bearer',
                'bearerFormat': 'JWT',
            }
        }
    },
}


