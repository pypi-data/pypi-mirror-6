import os
import sys
#from tempfile import gettempdir


BASE_DIR = os.path.dirname(os.path.dirname(__file__))

SECRET_KEY = 'LkfBr693tY3b2wL9a8XR8rrQmDxRKzPyPcQZ2Tz5JHKNaKEe'

USE_I18N = True
LANGUAGE_CODE = 'en'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:'
        #'NAME': os.path.join(
        #    gettempdir(), 'likert_field', 'tests', 'db.sqlite3'),
    }
}

INSTALLED_APPS = []
