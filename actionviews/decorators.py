from functools import update_wrapper


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
        @view_decorator
        def dummy(*args, **kwargs):
            pass

        update_wrapper(wrapper, dummy)

        # Need to preserve any existing attributes of 'func', including the name.
        update_wrapper(wrapper, func)

        return wrapper

    return decorator