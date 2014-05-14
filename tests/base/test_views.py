import pytest


@pytest.fixture(params=list(range(1)))
def TestView(request):
    from actionviews.base import ActionView

    class TestView(ActionView):

        def do_index(self):
            return {'result': 'test'}

    return [TestView][request.param]


@pytest.fixture
def django_request(request_factory):
    return request_factory.get('/')


def test_view(TestView, django_request):
    view = TestView.urls[0].callback
    response = view(django_request)
    assert response == {'result': 'test'}
