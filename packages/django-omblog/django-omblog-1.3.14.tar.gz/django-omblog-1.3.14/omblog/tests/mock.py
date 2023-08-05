from django.core.handlers.base import BaseHandler
from django.test.client import RequestFactory

import factory


class MockRequest(RequestFactory):
    def request(self, **request):
        request = RequestFactory.request(self, **request)
        handler = BaseHandler()
        handler.load_middleware()
        for mw in handler._request_middleware:
            if mw(request):
                raise Exception('middleware returned a response')
        return request


class PostFactory(factory.DjangoModelFactory):
    FACTORY_FOR = 'omblog.Post'
    title = factory.Sequence(lambda n: 'Blog Post {}'.format(n))
    slug = factory.Sequence(lambda n: 'blog-post-{}'.format(n))
    source_content = 'Blog Post'
    status = 3


class PostImageFactory(factory.DjangoModelFactory):
    FACTORY_FOR = 'omblog.PostImage'
    title = factory.Sequence(lambda n: 'Blog Post {}'.format(n))
    src = factory.Sequence(lambda n: 'fake/path/{}.png'.format(n))
