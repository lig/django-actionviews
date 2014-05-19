from django.conf.urls import patterns, url
from django.core.urlresolvers import RegexURLPattern, resolve
import pytest


@pytest.fixture(params=list(range(2)))
def TestView(request):
    from actionviews.base import View

    class TestView(View):

        def do_index(self:'', skip:r'\d+'=0):
            pass

        def do_detail(self, pk:r'\d+'):
            pass

        def do_article(self:'article', pk:r'\d+'):
            pass

        def do_default(self, pk):
            pass

    class PrefixView(View):
        action_method_prefix = 'act_'

        def act_index(self:'', skip:r'\d+'=0):
            pass

        def act_detail(self, pk:r'\d+'):
            pass

        def act_article(self:'article', pk:r'\d+'):
            pass

        def act_default(self, pk):
            pass

    return [TestView, PrefixView][request.param]


def test_urls(TestView):
    urls = TestView.urls

    assert all(map(lambda x: isinstance(x, RegexURLPattern), urls))

    urls_data = {url.name: url for url in urls}

    assert urls_data['index']._regex == r'^(skip/(?P<skip>\d+)/)?$'
    assert urls_data['detail']._regex == r'^detail/pk/(?P<pk>\d+)/$'
    assert urls_data['article']._regex == r'^article/pk/(?P<pk>\d+)/$'
    assert urls_data['default']._regex == r'^default/pk/(?P<pk>[\w\d]+)/$'

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
    assert urls_data['detail']._regex == r'^detail/(?P<pk>\d+)/$'
    assert urls_data['article']._regex == r'^article/(?P<pk>\d+)/$'
    assert urls_data['default']._regex == r'^default/(?P<pk>[\w\d]+)/$'

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
    assert urls_data['detail']._regex == r'^detail/pk/(?P<pk>\d+)/$'
    assert urls_data['article']._regex == r'^article/pk/(?P<pk>\d+)/$'
    assert urls_data['default']._regex == r'^default/pk/(?P<pk>\w+)/$'

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
            url(r'^detail/(?P<pk>\d+)/$', 'detail', name='detail'),
        )

    urls = CustomView.urls

    assert all(map(lambda x: isinstance(x, RegexURLPattern), urls))

    urls_data = {url.name: url for url in urls}

    assert urls_data['list']._regex == r'^(page/(?P<skip>\d+)/)?$'
    assert urls_data['detail']._regex == r'^detail/(?P<pk>\d+)/$'

    assert urls_data['list'].default_args == {'skip': 0}
    assert urls_data['detail'].default_args == {}

    assert 'index' not in urls_data
    assert 'article' not in urls_data
    assert 'default' not in urls_data


def test_urls_custom_actions(TestView):

    class CustomView(TestView):
        actions = {
            'list': '{}index'.format(TestView.action_method_prefix),
            'detail': '{}detail'.format(TestView.action_method_prefix),
        }

    urls = CustomView.urls

    assert all(map(lambda x: isinstance(x, RegexURLPattern), urls))

    urls_data = {url.name: url for url in urls}

    assert urls_data['list']._regex == r'^(skip/(?P<skip>\d+)/)?$'
    assert urls_data['detail']._regex == r'^detail/pk/(?P<pk>\d+)/$'

    assert urls_data['list'].default_args == {'skip': 0}
    assert urls_data['detail'].default_args == {}

    assert 'index' not in urls_data
    assert 'article' not in urls_data
    assert 'default' not in urls_data


def test_urls_child():
    from actionviews.base import View
    from actionviews.decorators import child_view

    class ChildView(View):

        def do_clist(self):
            pass

        def do_cdetail(self, child_id):
            pass

    class ParentView(View):

        @child_view(ChildView)
        def do_pdetail(self, parent_id=0):
            pass

    parent_urls = ParentView.urls

    assert (parent_urls[0]._regex ==
        r'^pdetail/(parent_id/(?P<parent_id>[\w\d]+)/)?')
    assert (
        parent_urls[0].default_kwargs['parent_action'].__name__ ==
        'do_pdetail')

    child_urls = parent_urls[0].url_patterns
    child_urls_data = {url.name: url for url in child_urls}

    assert child_urls_data['clist']._regex == r'^clist/$'
    assert (child_urls_data['cdetail']._regex ==
        r'^cdetail/child_id/(?P<child_id>[\w\d]+)/$')

    assert child_urls_data['clist'].default_args == {}
    assert child_urls_data['cdetail'].default_args == {}



def test_resolve_child(monkeypatch):
    from actionviews.base import View
    from actionviews.decorators import child_view

    class ChildView(View):

        def do_clist(self):
            pass

        def do_cdetail(self, child_id):
            pass

    class ParentView(View):

        def do_plist(self):
            pass

        @child_view(ChildView)
        def do_pdetail(self, parent_id):
            pass

    monkeypatch.setattr(
        'django.core.urlresolvers.get_urlconf',
        lambda: type(
            'urlconf', (), {
                'urlpatterns': patterns('', *ParentView.urls)}))

    assert resolve('/plist/').func.__name__ == 'do_plist'    
    assert resolve('/pdetail/parent_id/1/clist/').func.__name__ == 'do_clist'
