from pathlib import Path
import os
from dotenv import load_dotenv # Importação
import dj_database_url
from datetime import timedelta

# 1. Defina o BASE_DIR primeiro
BASE_DIR = Path(__file__).resolve().parent.parent

# 2. Carregue o .env usando o caminho absoluto
# Isso garante que ele ache o arquivo mesmo se você rodar o manage.py de outra pasta
load_dotenv(BASE_DIR / '.env')

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/6.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-%@@1m8v%d=cu%k86t7-0oqx7u86tgqx0x+hpr6qjwa8mhqogeg'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
# --- Bibliotecas de Terceiros (Libs instaladas) ---
    'rest_framework',   # Para criar a API
    'django_filters',   # Para os filtros na API
    'pwa',              # Para o aplicativo mobile/offline
    'corsheaders',      # <--- ADICIONADO (Para o React conversar com o Django)
    # --- Seus Apps ---
    'core',             # O coração do seu sistema
]

AUTH_USER_MODEL = 'core.UsuarioACS'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',  
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'smart_aps.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'smart_aps.wsgi.application'


# Database
# https://docs.djangoproject.com/en/6.0/ref/settings/#databases

DATABASES = {
    'default': dj_database_url.config(
        default=os.getenv('DATABASE_URL'),
        conn_max_age=600,
        conn_health_checks=True,
    )
}


# Password validation
# https://docs.djangoproject.com/en/6.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/6.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.0/howto/static-files/

STATIC_URL = 'static/'

# Redirecionamento após Login e Logout
LOGIN_REDIRECT_URL = 'index'  # Nome da rota da sua página inicial
LOGOUT_REDIRECT_URL = 'login' # Para onde vai quando sair

# CONFIGURAÇÕES DO PWA (Smart APS Mobile)
PWA_APP_NAME = 'Smart APS'
PWA_APP_DESCRIPTION = "Sistema de Controle de Vacinação"
PWA_THEME_COLOR = '#0d6efd' # Azul Bootstrap (cor da barra de status do Android)
PWA_BACKGROUND_COLOR = '#ffffff'
PWA_DISPLAY = 'standalone' # Isso faz sumir a barra do navegador (vira app mesmo)
PWA_SCOPE = '/'
PWA_START_URL = '/' # Quando abrir o app, vai pra Home

# Ícones (Você precisará colocar uma imagem logo.png na pasta static/images)
PWA_APP_ICONS = [
    {
        'src': '/static/images/wip.jpg',
        'sizes': '192x192'
    }
]
PWA_APP_ICONS_APPLE = [
    {
        'src': '/static/images/wip.jpg',
        'sizes': '512x512'
    }
]
PWA_SERVICE_WORKER_PATH = os.path.join(BASE_DIR, 'core/static/js/serviceworker.js')

# CONFIGURAÇÃO DE CORS (Para o React)
CORS_ALLOW_ALL_ORIGINS = False

CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173", # Porta padrão do Vite/React
    "http://127.0.0.1:5173",
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated', # Bloqueia tudo por padrão (segurança)
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10, 
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1),  # O usuario fica logado por 1 dia direto
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7), # Ele pode renovar sem senha por 7 dias
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': False,
    'AUTH_HEADER_TYPES': ('Bearer',),
}