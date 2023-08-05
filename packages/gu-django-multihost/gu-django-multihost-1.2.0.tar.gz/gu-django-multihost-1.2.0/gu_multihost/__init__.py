# Copyright (c) 2013 Andriy Gushuley
# Licensed under the terms of the MIT License (see LICENSE.txt)

from threading import currentThread
from django.conf import settings
from django.core.urlresolvers import reverse

MULTIHOST_DEFAULT_URLS = [
  'gu_multihost.urls',
]


def get_available_urls():
    return [(i, i) for i in getattr(settings, "MULTIHOST_AVAILABLE_URLS", MULTIHOST_DEFAULT_URLS)]


def is_database_driven_modules_urls():
    return getattr(settings, "MULTIHOST_DATABASE_DRIVEN_URLS", False)


__sites = {}
__default_site = None

def get_current_site():
    if currentThread() in __sites:
        return __sites[currentThread()]
    return None


def set_current_site(site):
    __sites[currentThread()] = site


def get_default_site(fail=False):
    global __default_site
    if not __default_site and fail:
        raise ValueError("Default site is not defined yet")
    return __default_site


def set_default_site(site):
    global __default_site
    __default_site = site


def mh_reverse(name, site, is_external=False, args=None, kwargs=None):
    if not site:
        site = get_current_site()

    urlconf = None if not site.urls_module else str(site.urls_module)
    url = reverse(name, urlconf=urlconf, args=args, kwargs=kwargs)
    if is_external or get_current_site() != site:
        return site.site.domain + url
    else:
        return url