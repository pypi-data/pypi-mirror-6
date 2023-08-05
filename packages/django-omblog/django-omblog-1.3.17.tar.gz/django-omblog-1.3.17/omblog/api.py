from tastypie.resources import ModelResource
from omblog.models import Post
print 'he'

class OMPostResource(ModelResource):

    class Meta:
        queryset = Post.objects.all()
        resource_name = 'posts'
