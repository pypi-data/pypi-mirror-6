from django.core.handlers.base import BaseHandler
from django.test.client import RequestFactory


class MockRequest(RequestFactory):
    def request(self, **request):
        request = RequestFactory.request(self, **request)
        handler = BaseHandler()
        handler.load_middleware()
        for mw in handler._request_middleware:
            if mw(request):
                raise Exception('middleware returned a response')
        return request
