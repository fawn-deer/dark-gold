from .common import *

ALLOWED_HOSTS += [
    '127.0.0.1'
]

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('DJANGO_SETTINGS_DARK_GOLD_SECRET_KEY',
                            '6$2pdw)gsz)g)*_g6*#dp4^f4h(kl6sl^k44p!z=r=or-#yh@$')

# prod database
DATABASES['default'] = {
    'ENGINE': 'django.db.backends.mysql',
    'NAME': os.environ.get('DJANGO_SETTINGS_DARK_GOLD_DATABASE_NAME', 'account_serve'),
    'USER': os.environ.get('DJANGO_SETTINGS_DARK_GOLD_DATABASE_USER', ''),
    'PASSWORD': os.environ.get('DJANGO_SETTINGS_DARK_GOLD_DATABASE_PASSWORD', ''),
    'HOST': os.environ.get('DJANGO_SETTINGS_DARK_GOLD_DATABASE_HOST', ''),
    'PORT': os.environ.get('DJANGO_SETTINGS_DARK_GOLD_DATABASE_PORT', ''),
}
