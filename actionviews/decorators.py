from functools import update_wrapper
from actionviews.base import View
from django.core.exceptions import ImproperlyConfigured


def action_decorator(view_decorator):

    def decorator(func):

        def wrapper(self, *args, **kwargs):

            @view_decorator
            def view_func(request, *view_args, **view_kwargs):
                return func(self, *view_args, **view_kwargs)

            return view_func(self.request, *args, **kwargs)

        # In case 'decorator' adds attributes to the function it decorates, we
        # want to copy those. We don't have access to bound_func in this scope,
        # but we can cheat by using it on a dummy function.
        update_wrapper(wrapper, view_decorator(lambda *args, **kwargs: None))

        # Need to preserve any existing attributes of 'func', including the name.
        update_wrapper(wrapper, func)

        return wrapper

    return decorator


def require_method(methods):

    if isinstance(methods, str):
        methods = [methods]

    def decorator(action):
        action.allowed_methods = methods
        return action

    return decorator


def child_view(view_klass):

    if not issubclass(view_klass, View):
        raise ImproperlyConfigured(
            '`child_view` decorator receive View subclass as its argument')

    def decorator(func):
        func.child_view = view_klass
        return func

    return decorator
