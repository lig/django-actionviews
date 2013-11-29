from django.conf.urls import patterns
from django.core.urlresolvers import RegexURLPattern
from actionviews.base import ActionView


def test_declaration():

    class TestView(ActionView):

        def do_index(self):
            pass

        def do_detail(self, id: '\d+'):
            pass

    urls = TestView.get_urls()
    assert all(map(lambda x: isinstance(x, RegexURLPattern), urls))
