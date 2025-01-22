"""
Django settings for eblog project.

Generated by 'django-admin startproject' using Django 5.0.6.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""
import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-(oma$ph=wzqf%&v40on7y+*qv3vml(x)m!^6te*n$1^aps=_k&'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*"]
CSRF_TRUSTED_ORIGINS = ['https://mfy.hwserver.cn', 'https://blog.hwserver.cn', 'https://ip.hwserver.cn']

# Application definition

# User
AUTH_USER_MODEL = "blog_auth.User"

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'blog',
    'blog_auth'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'eblog.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates']
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            # 配置静态文件
            'builtins': ['django.templatetags.static']
        },
    },
]

WSGI_APPLICATION = 'eblog.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        "HOST": "127.0.0.1",
        "PORT": 3306,
        'NAME': 'eblog',
        'USER': 'root',
        'PASSWORD': 'Tq@113211',
        'CREATE_DB': True,
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'zh-hans'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = '/static/'
# STATICFILES_DIRS = [
#     BASE_DIR / 'static',  # If you have a global static folder
# ]
STATIC_ROOT = BASE_DIR / 'static'

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# SMTP 服务器设置 (根据你的邮件服务提供商进行调整)
EMAIL_HOST = 'smtp.gmail.com'  # 例如 Gmail 的 SMTP 服务器地址
EMAIL_PORT = 587 #  994              # SMTP 端口号，587 是加密通信时的常用端口
EMAIL_USE_TLS = True         # 开启 TLS 加密
EMAIL_HOST_USER = 'mr.tongtsing@gmail.com'  # 你的邮件地址
EMAIL_HOST_PASSWORD = 'ahib elhb iltw dyss'  # OALZTAHNUMMEKROY你的邮箱密码或应用专用密码

# 默认发件人地址
DEFAULT_FROM_EMAIL = 'mr.tongtsing@gmail.com'

# 发送邮件时的默认回复地址
EMAIL_REPLY_TO = 'mr.tongtsing@gmail.com'

# 日志配置

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',  # 设置日志级别，可以是 DEBUG, INFO, WARNING, ERROR, CRITICAL
            'class': 'logging.FileHandler',
            'filename': '/tmp/eblog/eblog.log',  # 指定日志文件路径
            'formatter': 'verbose',
        },
        'console': {
            'level': 'ERROR',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],  # 配置输出到文件和控制台
            'level': 'INFO',  # 设置日志记录的最低级别
            'propagate': True,
        },
        'django.request': {
            'handlers': ['file', 'console'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
}

# 配置图片路径
MEDIA_URL = '/blog/media/'
MEDIA_ROOT = BASE_DIR / 'media/'

# 设置最大上传文件大小，单位是字节（例如：100MB）
DATA_UPLOAD_MAX_MEMORY_SIZE = 104857600  # 100MB

CORS_ALLOW_ALL_ORIGINS = True  # 允许所有来源的跨域请求
