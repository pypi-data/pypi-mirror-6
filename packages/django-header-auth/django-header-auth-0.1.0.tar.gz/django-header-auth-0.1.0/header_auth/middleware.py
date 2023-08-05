import logging

from django.http import HttpResponseForbidden
from django.utils.six import iteritems

from header_auth import settings


__all__ = [
    'HeaderAuthMiddleware',
]


class HeaderAuthMiddleware(object):

    def __init__(self, headers=None):
        self.headers = self.filter_headers(settings.HEADER_AUTH if headers is None else headers)

        if not self.headers:
            logger = logging.getLogger('django.request')
            logger.warning('HeaderAuthMiddleware is included, '
                           'but no headers are defined. '
                           'This may cause a false sense of security.')

    def process_request(self, request):
        if not self.authorize_headers(request):
            return self.get_unauthorized_response()

    def authorize_headers(self, request):
        """
        Authorizes the request's headers, returning `True` if they're ok,
        `False` otherwise.
        """
        for header, expected_value in iteritems(self.headers):
            if request.META.get(header) != expected_value:
                return False
        return True

    def get_unauthorized_response(self):
        """
        Returns the response for when the headers are incorrect. This is
        separated so it can eaily be customized in a subclass.
        """
        return HttpResponseForbidden()

    def filter_headers(self, headers):
        """
        Filters the defined headers, removing any empty values.
        """
        return {header: value for header, value in iteritems(headers) if value}
