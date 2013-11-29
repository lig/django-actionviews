import inspect
import logging

from django.conf.urls import url


logger = logging.getLogger('django.actionviews')


class ActionViewMeta(type):

    def __new__(cls, name, bases, attrs):
        # construct class to access parent attributes
        type_new = type.__new__(cls, name, bases, attrs)

        # get action_method_prefix
        action_method_prefix = type_new.action_method_prefix

        # find action names and corresponding methods
        actions = {}

        for attr_name in dir(type_new):

            if attr_name.startswith(action_method_prefix):
                action_name = attr_name[len(action_method_prefix):]

                # avoid empty action_name
                if action_name:
                    actions[action_name] = getattr(type_new, attr_name)

        type_new.actions = actions

        return type_new


class ActionView(metaclass=ActionViewMeta):

    action_method_prefix = 'do_'
    group_format = r'{group_name}/(?P<{group_name}>{group_regex})/'
    default_group_regex = r'[\w\d\S]+'

    @classmethod
    def get_urls(cls):
        urls = []

        for action_name, action_method in cls.actions.items():
            regex_chunks = []
            default_values = {}
            parameters = inspect.signature(action_method).parameters.values()

            for parameter in parameters:

                if parameter.name == 'self':
                    regex_chunks.append(
                        parameter.annotation is inspect._empty
                        and r'{}/'.format(action_name)
                        or parameter.annotation)
                    continue

                group_name = parameter.name

                if parameter.annotation is inspect._empty:
                    group_regex = cls.default_group_regex
                else:
                    group_regex = parameter.annotation

                if parameter.default is inspect._empty:
                    group_format = cls.group_format
                else:
                    default_values[parameter.name] = parameter.default
                    group_format = r'({})?'.format(cls.group_format)

                regex_chunks.append(group_format.format(
                    group_name=group_name, group_regex=group_regex))

            url_regex = r'^{}$'.format(''.join(regex_chunks))
            urls.append(url(
                regex=url_regex,
                view=None,
                kwargs=default_values,
                name=action_name))

        return urls
