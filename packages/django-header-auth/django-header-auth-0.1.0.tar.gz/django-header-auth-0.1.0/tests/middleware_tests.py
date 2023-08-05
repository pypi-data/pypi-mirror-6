from django.http import HttpResponseForbidden
from mock import *
from nose.tools import *

from header_auth.middleware import *


class TestHeaderAuthMiddleware(object):

    def test_noop(self):
        request = MagicMock()
        request.META = {}
        middleware = HeaderAuthMiddleware({})
        response = middleware.process_request(request)
        assert_is_none(response)

    def test_with_header(self):
        request = MagicMock()
        request.META = {'HTTP_X_SOME_HEADER': 'some_token', 'HTTP_X_ANOTHER_HEADER': 'another_token'}
        middleware = HeaderAuthMiddleware({'HTTP_X_SOME_HEADER': 'some_token'})
        response = middleware.process_request(request)
        assert_is_none(response)

    def test_without_header(self):
        request = MagicMock()
        request.META = {'HTTP_X_ANOTHER_HEADER': 'another_token'}
        middleware = HeaderAuthMiddleware({'HTTP_X_SOME_HEADER': 'some_token'})
        response = middleware.process_request(request)
        assert_is_instance(response, HttpResponseForbidden)

    def test_with_incorrect_header(self):
        request = MagicMock()
        request.META = {'HTTP_X_SOME_HEADER': 'another_token'}
        middleware = HeaderAuthMiddleware({'HTTP_X_SOME_HEADER': 'some_token'})
        response = middleware.process_request(request)
        assert_is_instance(response, HttpResponseForbidden)

    def test_with_empty_defined_header(self):
        request = MagicMock()
        request.META = {'HTTP_X_SOME_HEADER': 'another_token'}
        middleware = HeaderAuthMiddleware({'HTTP_X_SOME_HEADER': ''})
        response = middleware.process_request(request)
        assert_is_none(response)

    def test_gets_defined_headers_from_settings(self):
        request = MagicMock()
        request.META = {}
        middleware = HeaderAuthMiddleware()
        response = middleware.process_request(request)
        assert_is_instance(response, HttpResponseForbidden)
