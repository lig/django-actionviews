from django.http.response import HttpResponseBase
from django.core.exceptions import ImproperlyConfigured


class ActionResponse(Exception):

    def __init__(self, response):

        if not isinstance(response, HttpResponseBase):
            raise ImproperlyConfigured(
                'ActionResponse argument must be HttpResponseBase instance')

        self.response = response
