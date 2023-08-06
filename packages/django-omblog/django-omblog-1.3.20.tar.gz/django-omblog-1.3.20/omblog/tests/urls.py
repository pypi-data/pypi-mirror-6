from django.conf.urls import (
    include,
    patterns)

urlpatterns = patterns(
    '',
    (r'blog/', include('omblog.urls', namespace='omblog')),
)
