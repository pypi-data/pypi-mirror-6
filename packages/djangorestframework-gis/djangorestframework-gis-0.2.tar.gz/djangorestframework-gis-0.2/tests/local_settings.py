from settings import *

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'django_restframework_gis',
        'USER': 'postgres',
        'PASSWORD': 'password',
        'HOST': '127.0.0.1',
        'PORT': '5432'
    },
}

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.gis',
    
    # geodjango widgets
    #'olwidget',
    
    # admin
    #'grappelli',
    'django.contrib.admin',
    
    # rest framework
    'rest_framework',
    'rest_framework_gis',
    
    # test app
    'django_restframework_gis_tests'
)
