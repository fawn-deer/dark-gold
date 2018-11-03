from .dev import *

ALLOWED_HOSTS = ['*']

# test database
DATABASES['default'] = {
    'ENGINE': 'django.db.backends.sqlite3',
    'TEST': {
        'NAME': os.path.join(BASE_DIR, 'test-db.sqlite3'),
        # 'NAME': 'test-db.sqlite3'
    }
}
