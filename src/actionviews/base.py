import logging

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

    action_field_name = '_action'
    action_method_prefix = 'do_'

    @classmethod
    def get_urls(cls):
        print(cls.actions)
