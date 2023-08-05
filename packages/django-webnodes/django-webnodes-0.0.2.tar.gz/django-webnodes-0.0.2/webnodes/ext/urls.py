from django.conf.urls.defaults import patterns, url

from .views import WebNode

urlpatterns = patterns('',
    url('^(?P<node_name>[^/]+)', WebNode.as_view())
)
