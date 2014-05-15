from functools import partial
import inspect
import logging

from django.conf.urls import url
from django.http.response import HttpResponseNotAllowed, HttpResponse
from django.utils.decorators import classonlymethod


logger = logging.getLogger('django.actionviews')


class ActionViewMeta(type):

    def __new__(cls, name, bases, attrs):
        # construct class to access parent attributes
        type_new = type.__new__(cls, name, bases, attrs)

        # get action_method_prefix
        action_method_prefix = type_new.action_method_prefix

        # find action names and corresponding methods or use defined map
        if 'actions' in attrs:
            actions = {name: getattr(type_new, attr_name)
                for name, attr_name in attrs['actions'].items()}
        else:
            actions = {}

            for attr_name in dir(type_new):

                if attr_name.startswith(action_method_prefix):
                    action_name = attr_name[len(action_method_prefix):]

                    # avoid empty action_name
                    if action_name:
                        actions[action_name] = getattr(type_new, attr_name)

        type_new.actions = actions

        # construct urls if there is no custom urls defined
        if 'urls' not in attrs:
            urls = []

            for action_name, action_method in type_new.actions.items():
                regex_chunks = []
                default_values = {}
                parameters = inspect.signature(
                    action_method).parameters.values()

                for parameter in parameters:

                    if parameter.name == 'self':
                        group_name = (parameter.annotation is inspect._empty
                            and action_name
                            or parameter.annotation)
                        sep = group_name and '/'
                        regex_chunks.append(r'{}{}'.format(group_name, sep))
                        continue

                    group_name = parameter.name

                    if parameter.annotation is inspect._empty:
                        group_regex = type_new.default_group_regex
                    else:
                        group_regex = parameter.annotation

                    if parameter.default is inspect._empty:
                        group_format = type_new.group_format
                    else:
                        default_values[parameter.name] = parameter.default
                        group_format = r'({})?'.format(type_new.group_format)

                    regex_chunks.append(group_format.format(
                        group_name=group_name, group_regex=group_regex))

                url_regex = r'^{}$'.format(''.join(regex_chunks))
                urls.append(url(
                    regex=url_regex,
                    view=type_new.as_view(action_method),
                    kwargs=default_values,
                    name=action_name))

            type_new.urls = urls

        return type_new


class ActionView(metaclass=ActionViewMeta):

    action_method_prefix = 'do_'
    group_format = r'{group_name}/(?P<{group_name}>{group_regex})/'
    default_group_regex = r'[\w\d\S]+'

    http_method_names = ['get', 'post', 'put', 'patch', 'delete', 'head',
        'options', 'trace']

    @classonlymethod
    def as_view(cls, action):  # @NoSelf
        """
        Action method to view factory.
        """

        def view(request, *args, **kwargs):
            # get view class instance
            self = cls()

            # set instance attributes
            if hasattr(self, 'get') and not hasattr(self, 'head'):
                self.head = self.get
            self.request = request
            self.args = args
            self.kwargs = kwargs

            # dispatch action 
            return self.dispatch(action, *args, **kwargs)

        return view

    def dispatch(self, action, *args, **kwargs):
        """Try to dispatch to the right action; defer to the error handler if
        the request method isn't on the approved list.
        """
        http_method_names = getattr(
            action, 'allowed_methods', self.http_method_names)

        if self.request.method.lower() in http_method_names:
            handler = getattr(
                self,
                self.request.method.lower(),
                self.http_method_not_allowed)
        else:
            handler = self.http_method_not_allowed
        return handler(action, *args, **kwargs)

    def http_method_not_allowed(self, action, *args, **kwargs):
        logger.warning(
            'Method Not Allowed (%s): %s',
            self.request.method,
            self.request.path,
            extra={
                'status_code': 405,
                'request': self.request
            }
        )
        return HttpResponseNotAllowed(self._allowed_methods(action))

    def options(self, action, *args, **kwargs):
        """
        Handles responding to requests for the OPTIONS HTTP verb.
        """
        response = HttpResponse()
        response['Allow'] = ', '.join(self._allowed_methods(action))
        response['Content-Length'] = '0'
        return response

    def _allowed_methods(self, action):
        return map(
            str.upper,
            filter(
                partial(hasattr, self),
                getattr(action, 'allowed_methods', self.http_method_names)))
