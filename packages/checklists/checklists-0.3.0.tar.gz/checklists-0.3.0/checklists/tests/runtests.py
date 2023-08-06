#!/usr/bin/env python
import os
import sys
import tempfile

from django.conf import settings


if not settings.configured:
    base_path = os.path.abspath(os.path.dirname(__file__))
    settings.configure(
        LANGUAGES=(
            ('en', u'English'),
        ),
        LANGUAGE_CODE='en',
        TRANSMETA_DEFAULT_LANGUAGE='en',
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': 'db.sqlite',
            }
        },
        INSTALLED_APPS=[
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'transmeta',
            'checklists',
        ],
        BASE_PATH=base_path,
        TEST_DISCOVERY_ROOT=os.path.join(base_path, os.pardir),
        TEST_RUNNER="checklists.tests.runner.DiscoveryRunner",
        APP_ROOT=os.path.join(base_path, os.pardir, os.pardir),
        CHECKLISTS_DOWNLOAD_DIR='',
        CHECKLISTS_REPORT_RECIPIENTS='admins@example.com',
    )


def runtests(*test_args):
    from django.test.utils import get_runner
    TestRunner = get_runner(settings)
    test_runner = TestRunner(verbosity=1, interactive=False)
    failures = test_runner.run_tests(['checklists.tests'])
    sys.exit(failures)


if __name__ == '__main__':
    runtests(*sys.argv[1:])