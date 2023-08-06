import sys
from django.conf import settings

settings.configure(
    DEBUG=True,
    DATABASES={
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
        }
    },
    ROOT_URLCONF='myapp.urls',
    INSTALLED_APPS=(
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.staticfiles',
        'django.contrib.sessions',
        'django.contrib.admin',
        'django.contrib.sites',
        'cms',
        'mptt',
        'south',
        'djangocms_file',
    ),
    TEMPLATE_CONTEXT_PROCESSORS=(
        'django.core.context_processors.request',
    ),
    SITE_ID=1,
    LANGUAGE_CODE='en',
    LANGUAGES=(('en','English'),),
    STATIC_URL='/static/',
    CMS_TEMPLATES = [
        ('dummy.html', 'Dummy'),
    ],

)
from django.test.simple import DjangoTestSuiteRunner

test_runner = DjangoTestSuiteRunner(verbosity=1)
from south.management.commands import patch_for_test_db_setup
patch_for_test_db_setup()
failures = test_runner.run_tests(['djangocms_file', ])
if failures:
    sys.exit(failures)

