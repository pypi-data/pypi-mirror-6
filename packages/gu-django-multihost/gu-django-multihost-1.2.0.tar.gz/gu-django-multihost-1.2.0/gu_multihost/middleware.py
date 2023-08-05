import re
from django.contrib import sites
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponsePermanentRedirect
from django.utils import cache
from django.conf import settings
from . import models, get_default_site, set_default_site, set_current_site


def _process_request(request):
    if not get_default_site():
        set_default_site(models.Site(
            site=sites.models.Site.objects.get(id=settings.SITE_ID)
        ))

    _host = request.META["HTTP_HOST"]
    site = None
    for host in models.Site.objects.order_by("order").all():
        r = re.compile(host.host_regexp)
        if r.match(_host):
            if host.urls_module:
                setattr(request, "urlconf", str(host.urls_module))
            else:
                if hasattr(request, "urlconf"):
                    delattr(request, "urlconf")
            site = host
            break
        elif _host.startswith("www.") and r.match(_host[4:]):
            path = u'%s%s' % (host.site.domain, request.META["PATH_INFO"],)
            if request.META["QUERY_STRING"]:
                path = u'%s?%s' % (path, request.META["QUERY_STRING"], )
            return HttpResponsePermanentRedirect(path)

    if not site:
        try:
            site = models.Site.objects.get(site__id__exact=settings.SITE_ID)
        except ObjectDoesNotExist:
            site = get_default_site()

    set_current_site(site)
        #def process_request


class MultiHostMiddleware:
    def __init__(self):
        pass

    def process_request(self, request):
        return _process_request(request)

    def process_response(self, request, response):
        cache.patch_vary_headers(response, ('Host',))
        return response