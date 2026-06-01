"""
Configuracion de Django para el proyecto SoundStream.
Fase 4 - Proyecto Integrador.
"""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-soundstream-fase4-cambia-esto-en-produccion'
DEBUG = True
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'apps.catalogo',
    'apps.operacion',
    'apps.usuarios',
    'apps.web',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'soundstream.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.messages.context_processors.messages',
                'apps.web.context_processors.branding',
                'apps.usuarios.auth.usuario_actual',
            ],
        },
    },
]

WSGI_APPLICATION = 'soundstream.wsgi.application'

# ---------------------------------------------------------------------------
# BASE DE DATOS - SQL Server (Fase 3)
# ---------------------------------------------------------------------------
# Cambia 'localhost\\SQLEXPRESS' por tu instancia real.
# Si usas autenticacion de Windows deja USER y PASSWORD vacios y agrega
# 'Trusted_Connection': 'yes' en OPTIONS.

# Conexion a la instancia local SQL Server Express con autenticacion de Windows.
# Si prefieres el login SQL del equipo, comenta 'trusted_connection' y agrega
# 'USER' / 'PASSWORD' (p. ej. AbelRamosLogin). Ajusta HOST a tu instancia.
DATABASES = {
    'default': {
        'ENGINE': 'mssql',
        'NAME': 'SoundStreamDB',
        'HOST': r'localhost\SQLEXPRESS',
        'PORT': '',
        'OPTIONS': {
            'driver': 'ODBC Driver 17 for SQL Server',
            'trusted_connection': 'yes',
            'extra_params': 'TrustServerCertificate=yes;',
        },
    }
}

LANGUAGE_CODE = 'es-mx'
TIME_ZONE = 'America/Mexico_City'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

FIXTURE_DIRS = [BASE_DIR / 'fixtures']

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
