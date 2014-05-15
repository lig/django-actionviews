import sys

from django.conf import settings
import pytest
from os import path


sys.path[0:0] = ['']


@pytest.fixture(scope='session', autouse=True)
def django_settings():
    settings.configure(
        DATABASES={'default': {'ENGINE': 'django.db.backends.dummy'}},
        TEMPLATE_DIRS=(path.join(path.dirname(__file__), 'templates'),),
    )


@pytest.fixture(scope='session')
def request_factory(django_settings):
    from django.test.client import RequestFactory
    return RequestFactory()
