import pytest
from functools import wraps
from actionviews.base import TemplateResponseMixin
from django.conf.urls import patterns


@pytest.fixture(params=list(range(1)))
def TestView(request):
    from actionviews.base import ActionView

    class TestView(ActionView):

        def do_index(self:''):
            return {'result': 'test'}

    return [TestView][request.param]


@pytest.fixture
def django_request(request_factory):
    return request_factory.get('/')


def test_view(TestView, django_request):

    class TestGetView(TestView):

        def get(self, request):
            return self.action()

    view = TestGetView.urls[0].callback
    response = view(django_request)
    assert response == {'result': 'test'}


def test_decorated_action_on_view(TestView, django_request):

    def test_decorator(func):
        func.is_decorated = True
        return func

    class TestGetView(TestView):

        def get(self, request):
            assert self.action.is_decorated

        @test_decorator
        def do_index(self):
            return {'result': 'test'}

    view = TestGetView.urls[0].callback
    view(django_request)


def test_default_template_name(TestView, django_request, monkeypatch):

    class TestGetView(TestView, TemplateResponseMixin):

        def get(self, request):
            assert self.get_template_names() == ['/TestGetView/index.html']

    monkeypatch.setattr(
        'django.core.urlresolvers.get_urlconf',
        lambda: type(
            'urlconf', (), {'urlpatterns': patterns('', *TestGetView.urls)}))

    view = TestGetView.urls[0].callback
    view(django_request)
