def test_action_decorator():
    from actionviews.decorators import action_decorator

    decorator_request = []

    def view_decorator(func):

        def wrapper(request, *args, **kwargs):
            decorator_request.append(request)
            return func(request, *args, **kwargs)

        wrapper.is_decorated = True

        return wrapper

    class View:

        def __init__(self):
            self.request = 'Request'

        @action_decorator(view_decorator)
        def method(self, *args, **kwargs):
            return self.request

    view = View()

    assert view.method() == 'Request'
    assert decorator_request == ['Request']
    assert view.method.is_decorated
