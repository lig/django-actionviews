from django.conf.urls import patterns
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import resolve
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


@pytest.fixture
def django_request_options(request_factory):
    return request_factory.options('/')


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


def test_options_method(TestView, django_request_options):
    view = TestView.urls[0].callback
    response = view(django_request_options)
    assert response.status_code == 200
    assert response['Allow'] == 'OPTIONS'
    assert response['Content-Length'] == '0'


def test_child(monkeypatch, django_request):
    from actionviews.base import View, TemplateView
    from actionviews.decorators import child_view

    class ChildView(TemplateView):

        def do_index(self:''):
            return {'result': 'test'}

    class ParentView(View):

        @child_view(ChildView)
        def do_index(self:''):
            pass

    monkeypatch.setattr(
        'django.core.urlresolvers.get_urlconf',
        lambda: type(
            'urlconf', (), {
                'urlpatterns': patterns('', *ParentView.urls)}))

    view = resolve('/').func
    response = view(django_request)

    assert response.rendered_content == 'test'


def test_child_defaults_for_parent(monkeypatch, request_factory):
    from actionviews.base import View, TemplateView
    from actionviews.decorators import child_view

    class ChildView(TemplateView):

        def do_index(self):
            return {}

    class ParentView(View):

        @child_view(ChildView)
        def do_pindex(self, result='test'):
            return {'result': result}

    monkeypatch.setattr(
        'django.core.urlresolvers.get_urlconf',
        lambda: type(
            'urlconf', (), {
                'urlpatterns': patterns('', *ParentView.urls)}))

    resolver_match = resolve('/pindex/result/test/index/')
    response = resolver_match.func(
        request_factory.get('/pindex/result/test/index/'),
        **resolver_match.kwargs)

    assert response.rendered_content == 'test'


def test_raise_response_from_action(django_request, monkeypatch):
    from django.http.response import HttpResponse
    from actionviews.base import TemplateView
    from actionviews.exceptions import ActionResponse

    class TestView(TemplateView):

        def do_index(self:''):
            raise ActionResponse(HttpResponse())

    monkeypatch.setattr(
        'django.core.urlresolvers.get_urlconf',
        lambda: type(
            'urlconf', (), {
                'urlpatterns': patterns('', *TestView.urls)}))

    view = resolve('/').func
    response = view(django_request)

    assert response.status_code == 200


def test_raise_non_response_from_action(django_request, monkeypatch):
    from actionviews.base import TemplateView
    from actionviews.exceptions import ActionResponse

    class TestView(TemplateView):

        def do_index(self:''):
            raise ActionResponse({})

    monkeypatch.setattr(
        'django.core.urlresolvers.get_urlconf',
        lambda: type(
            'urlconf', (), {
                'urlpatterns': patterns('', *TestView.urls)}))

    view = resolve('/').func

    with pytest.raises(ImproperlyConfigured):
        view(django_request)


def test_return_response_from_action(django_request, monkeypatch):
    from django.http.response import HttpResponse
    from actionviews.base import TemplateView

    class TestView(TemplateView):

        def do_index(self:''):
            return HttpResponse()

    monkeypatch.setattr(
        'django.core.urlresolvers.get_urlconf',
        lambda: type(
            'urlconf', (), {
                'urlpatterns': patterns('', *TestView.urls)}))

    view = resolve('/').func
    response = view(django_request)

    assert response.status_code == 200
