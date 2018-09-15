from .common import *
from .dev import *

# test database
DATABASES['default'] = {
    'ENGINE': 'django.db.backends.sqlite3',
    'NAME': os.path.join(BASE_DIR, 'test-db.sqlite3'),
}
