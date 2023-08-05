try:
    from django.conf.urls import handler404, handler500, patterns,\
    url
except ImportError:
    from django.conf.urls.defaults import handler404, handler500, patterns,\
    url
from django.http import HttpResponsePermanentRedirect
from . import get_default_site


def redirect(req, path):
    return HttpResponsePermanentRedirect(u'%s/%s' % (get_default_site().site.domain, path,))

urlpatterns = patterns('',
     url(r'^(?P<path>.*)$', redirect),
)
