gu-django-multihost
===

**gu-django-multihost** is a Django application/framework which allow to serve different hostnames "
                  "and urlconfs in one django application instance
Quickstart:
===

Install gu-django-multihost:

    $ pip install gu-django-multihost

Add gu-multihost to INSTALLED_APPS in settings.py for your project:

    INSTALLED_APPS = (
        ...
        'gu_multihost',
    )

    #multihost
    MULTIHOST_DATABASE_DRIVEN_URLS = True # means that list or url modules are stored in database and managed there

    #for MULTIHOST_DATABASE_DRIVEN_URLS = False make a list possilbe selections for sites urls
    from gu_multihost import MULTIHOST_DEFAULT_URLS
    MULTIHOST_AVAILABLE_URLS = MULTIHOST_DEFAULT_URLS + [ROOT_URLCONF, ]

Add middleware class fetch from cache middleware :

    MIDDLEWARE_CLASSES += (
        # should be called after FetchFromCacheMiddleware
        'gu_multihost.middleware.MultiHostMiddleware',
        'django.middleware.cache.FetchFromCacheMiddleware',
        )

Setup you'r multihost sites objects.

Standard core django sites host names should be configured to actual accesible domain names with protocol name and port values without ending slash:

    https://site-name.org:8433

In your code:

    import gu_multihost

Yu can query current site, which serves a request:

    gu_multihost.get_current_site.site # link to django site object

You can build urls for different sites with a full url.

    gu_multihost.mh_reverse(news_item, site=None, full_url=False, [site.two_letter_code, nid])

Build short url for default site - /BB/news/item/XXX/

    gu_multihost.mh_reverse(news_item, site=None, full_url=False, [site.two_letter_code, nid])

Build full url for default site - http://default.site/BB/news/item/XXX/

    gu_multihost.mh_reverse(news_item, site=mobile, full_url=False, [site.two_letter_code, nid])

Build full url for separate site - http://mobile.site/BB/ni/XXX/

The same is from django templates:

    {% import multihost %}

    {% mh_reverse 'portal-news-item' '' 'pb' %}
    {% mh_reverse 'portal-news-item' 'mobile' 'pb' %}

License (and related information):
===
Originally written by Andriy Gushuley.

This program is licensed under the MIT License (see LICENSE.txt)