import os
import sys

from django.conf import settings
from django.core.management import call_command
from django.db.models import loading
from django import test


sys.path.append(os.path.dirname(__file__))


class CustomTestCase(test.TestCase):
    apps = ('likert_test_app',)

    def _pre_setup(self):
        # Add the models to the db.
        self._original_installed_apps = list(settings.INSTALLED_APPS)
        for app in self.apps:
            settings.INSTALLED_APPS.append(app)
        loading.cache.loaded = False
        call_command('syncdb', interactive=False, verbosity=1)
        # Call the original method that does the fixtures etc.
        super(CustomTestCase, self)._pre_setup()

    def _post_teardown(self):
        # Call the original method.
        super(CustomTestCase, self)._post_teardown()
        # Restore the settings.
        settings.INSTALLED_APPS = self._original_installed_apps
        loading.cache.loaded = False
