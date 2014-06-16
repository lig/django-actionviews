from django.conf.urls import patterns
from django.core.exceptions import ImproperlyConfigured
import pytest


def test_action_decorator():
    from actionviews.decorators import action_decorator

    decorator_request = []

    def view_decorator(func):

        def wrapper(request, *args, **kwargs):
            decorator_request.append(request)
            return func(request, *args, **kwargs)

        wrapper.is_decorated = True

        return wrapper

    class View:

        def __init__(self):
            self.request = 'Request'

        @action_decorator(view_decorator)
        def method(self, *args, **kwargs):
            return self.request

    view = View()

    assert view.method() == 'Request'
    assert decorator_request == ['Request']
    assert view.method.is_decorated


@pytest.mark.parametrize('decorator_arg,allowed_methods', [
    ('post', ['post']),
    (['post'], ['post']),
    (['post', 'put'], ['post', 'put']),
])
def test_require_method(decorator_arg, allowed_methods):
    from actionviews.decorators import require_method

    class View:

        def __init__(self):
            self.request = 'Request'

        @require_method(decorator_arg)
        def action(self, *args, **kwargs):
            return self.request

    view = View()

    assert view.action.allowed_methods == allowed_methods


def test_child_view():
    from actionviews.base import View
    from actionviews.decorators import child_view

    class ChildView(View):
        pass

    class ParentView(View):

        @child_view(ChildView)
        def do_index(self):
            pass

    parent_view = ParentView()

    assert parent_view.do_index.child_view == ChildView


def test_child_view_not_view():
    from actionviews.base import View
    from actionviews.decorators import child_view

    class ChildView:
        pass

    class ParentView(View):

        with pytest.raises(ImproperlyConfigured):
            @child_view(ChildView)
            def do_index(self):
                pass


def test_form_decorator(request_factory, monkeypatch):
    from django import forms
    from actionviews.base import DummyView
    from actionviews.decorators import form

    class TestForm(forms.Form):
        field = forms.CharField()

    class TestView(DummyView):

        @form(TestForm)
        def do_update(self:''):
            return {'result': self.form.is_valid()}

    monkeypatch.setattr(
        'django.core.urlresolvers.get_urlconf',
        lambda: type(
            'urlconf', (), {
                'urlpatterns': patterns('', *TestView.urls)}))

    view = TestView.urls[0].callback
    response = view(request_factory.post('/', data={'field': 'value'}))
    assert response['result']
