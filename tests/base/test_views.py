from django.conf.urls import patterns
import pytest

from actionviews.base import TemplateResponseMixin
from actionviews.decorators import require_method


@pytest.fixture(params=list(range(1)))
def TestView(request, monkeypatch):
    from actionviews.base import View

    class TestView(View):

        def do_index(self:''):
            return {'result': 'test'}

    monkeypatch.setattr(
        'django.core.urlresolvers.get_urlconf',
        lambda: type(
            'urlconf', (), {'urlpatterns': patterns('', *TestView.urls)}))

    return [TestView][request.param]


@pytest.fixture
def django_request(request_factory):
    return request_factory.get('/')


@pytest.fixture
def django_request_post(request_factory):
    return request_factory.post('/')


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


def test_default_template_name(TestView, django_request):

    class TestGetView(TestView, TemplateResponseMixin):

        def get(self, request):
            assert self.get_template_names() == ['TestGetView/index.html']

    view = TestGetView.urls[0].callback
    view(django_request)


def test_template_view(django_request, monkeypatch):
    from actionviews.base import TemplateView

    class TestTemplateView(TemplateView):

        def do_index(self:''):
            return {'result': 'test'}

    monkeypatch.setattr(
        'django.core.urlresolvers.get_urlconf',
        lambda: type(
            'urlconf', (), {
                'urlpatterns': patterns('', *TestTemplateView.urls)}))

    view = TestTemplateView.urls[0].callback
    response = view(django_request)
    assert response.rendered_content == 'test'


def test_method_allowed(TestView, django_request_post, monkeypatch):
    from actionviews.base import TemplateView

    class TestPostView(TemplateView):

        @require_method('post')
        def do_index(self:''):
            return {'result': 'test'}

    monkeypatch.setattr(
        'django.core.urlresolvers.get_urlconf',
        lambda: type(
            'urlconf', (), {
                'urlpatterns': patterns('', *TestPostView.urls)}))

    view = TestPostView.urls[0].callback
    response = view(django_request_post)
    assert response.status_code == 200
    assert response.rendered_content == 'test'


def test_method_not_allowed(django_request, monkeypatch):
    from actionviews.base import TemplateView

    class TestPostView(TemplateView):

        @require_method('post')
        def do_index(self:''):
            return {'result': 'test'}

    monkeypatch.setattr(
        'django.core.urlresolvers.get_urlconf',
        lambda: type(
            'urlconf', (), {
                'urlpatterns': patterns('', *TestPostView.urls)}))

    view = TestPostView.urls[0].callback
    response = view(django_request)
    assert response.status_code == 405
