import os

DJANGO_SETTINGS_ENVIRONMENT = os.environ.get('DJANGO_SETTINGS_DARK_GOLD_ENVIRONMENT', 'Not Found Environment')
if DJANGO_SETTINGS_ENVIRONMENT == 'dev':
    from .setting.dev import *
elif DJANGO_SETTINGS_ENVIRONMENT == 'prod':
    from .setting.prod import *
elif DJANGO_SETTINGS_ENVIRONMENT == 'test':
    from .setting.test import *
else:
    from .setting.dev import *
