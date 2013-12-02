import pytest
from operator import attrgetter

from django.core.urlresolvers import RegexURLPattern
from django.conf.urls import patterns, url

from actionviews.base import ActionView


@pytest.fixture(params=list(range(2)))
def TestView(request):

    class TestView(ActionView):

        def do_index(self:'', skip:r'\d+'=0):
            pass

        def do_detail(self, id:r'\d+'):
            pass

        def do_article(self:'article', id:r'\d+'):
            pass

        def do_default(self, id):
            pass

    class PrefixView(ActionView):
        action_method_prefix = 'act_'

        def act_index(self:'', skip:r'\d+'=0):
            pass

        def act_detail(self, id:r'\d+'):
            pass

        def act_article(self:'article', id:r'\d+'):
            pass

        def act_default(self, id):
            pass

    return [TestView, PrefixView][request.param]


def test_urls(TestView):
    urls = TestView.urls

    assert all(map(lambda x: isinstance(x, RegexURLPattern), urls))

    urls_data = {url.name: url for url in urls}

    assert urls_data['index']._regex == r'^(skip/(?P<skip>\d+)/)?$'
    assert urls_data['detail']._regex == r'^detail/id/(?P<id>\d+)/$'
    assert urls_data['article']._regex == r'^article/id/(?P<id>\d+)/$'
    assert urls_data['default']._regex == r'^default/id/(?P<id>[\w\d\S]+)/$'

    assert urls_data['index'].default_args == {'skip': 0}
    assert urls_data['detail'].default_args == {}
    assert urls_data['article'].default_args == {}
    assert urls_data['default'].default_args == {}


def test_urls_format(TestView):

    class FormatView(TestView):
        group_format = r'(?P<{group_name}>{group_regex})/'

    urls = FormatView.urls

    assert all(map(lambda x: isinstance(x, RegexURLPattern), urls))

    urls_data = {url.name: url for url in urls}

    assert urls_data['index']._regex == r'^((?P<skip>\d+)/)?$'
    assert urls_data['detail']._regex == r'^detail/(?P<id>\d+)/$'
    assert urls_data['article']._regex == r'^article/(?P<id>\d+)/$'
    assert urls_data['default']._regex == r'^default/(?P<id>[\w\d\S]+)/$'

    assert urls_data['index'].default_args == {'skip': 0}
    assert urls_data['detail'].default_args == {}
    assert urls_data['article'].default_args == {}
    assert urls_data['default'].default_args == {}


def test_urls_default(TestView):

    class FormatView(TestView):
        default_group_regex = r'\w+'

    urls = FormatView.urls

    assert all(map(lambda x: isinstance(x, RegexURLPattern), urls))

    urls_data = {url.name: url for url in urls}

    assert urls_data['index']._regex == r'^(skip/(?P<skip>\d+)/)?$'
    assert urls_data['detail']._regex == r'^detail/id/(?P<id>\d+)/$'
    assert urls_data['article']._regex == r'^article/id/(?P<id>\d+)/$'
    assert urls_data['default']._regex == r'^default/id/(?P<id>\w+)/$'

    assert urls_data['index'].default_args == {'skip': 0}
    assert urls_data['detail'].default_args == {}
    assert urls_data['article'].default_args == {}
    assert urls_data['default'].default_args == {}


def test_urls_custom(TestView):

    class CustomView(TestView):
        urls = patterns('',
            # @todo: check for correct view
            url(r'^(page/(?P<skip>\d+)/)?$',
                'index',
                kwargs={'skip': 0},
                name='list'),
            url(r'^detail/(?P<id>\d+)/$', 'detail', name='detail'),
        )

    urls = CustomView.urls

    assert all(map(lambda x: isinstance(x, RegexURLPattern), urls))

    urls_data = {url.name: url for url in urls}

    assert urls_data['list']._regex == r'^(page/(?P<skip>\d+)/)?$'
    assert urls_data['detail']._regex == r'^detail/(?P<id>\d+)/$'

    assert urls_data['list'].default_args == {'skip': 0}
    assert urls_data['detail'].default_args == {}

    assert 'index' not in urls_data
    assert 'article' not in urls_data
    assert 'default' not in urls_data
