from .common import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '6$2pdw)gsz)g)*_g6*#dp4^f4h(kl6sl^k44p!z=r=or-#yh@$'

DEBUG = True

# dev database
DATABASES['default'] = {
    'ENGINE': 'django.db.backends.sqlite3',
    'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
}
