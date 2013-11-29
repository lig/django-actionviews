from operator import attrgetter

from django.core.urlresolvers import RegexURLPattern
from django.conf.urls import patterns

from actionviews.base import ActionView


def test_declaration():

    class TestView(ActionView):

        def do_index(self:'', skip:r'\d+'=0):
            pass

        def do_detail(self, id:r'\d+'):
            pass

    urls = TestView.get_urls()

    assert all(map(lambda x: isinstance(x, RegexURLPattern), urls))

    urls_data = {url.name: url for url in urls}

    assert urls_data['index']._regex == r'^(skip/(?P<skip>\d+)/)?$'
    assert urls_data['detail']._regex == r'^detail/id/(?P<id>\d+)/$'

    assert urls_data['index'].default_args == {'skip': 0}
    assert urls_data['detail'].default_args == {}
