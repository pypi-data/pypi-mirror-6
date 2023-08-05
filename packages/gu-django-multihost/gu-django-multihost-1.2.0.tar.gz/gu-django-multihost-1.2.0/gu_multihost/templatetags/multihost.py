
from django import template
from django.template import TemplateSyntaxError, Node
from django.contrib.sites import models as sites_models
import re
from django.template.base import FilterExpression
from django.utils.encoding import smart_str
from .. import mh_reverse
from .. import models


class MHReverseNode(Node):
    def __init__(self, view_name, site, args, kwargs, as_var):
        self.view_name = view_name
        self.args = args
        self.site = site
        self.as_var = as_var
        self.kwargs = kwargs

    def render(self, context):
        args = [arg.resolve(context) for arg in self.args]
        view = self.view_name.resolve(context)
        if isinstance(self.site, FilterExpression):
            site = self.site.resolve(context)
        else:
            site = self.site
        site = site or None  # avoid '' values
        if isinstance(site, basestring) or isinstance(site, unicode):
            site = sites_models.Site.objects.get(name=site)
            site = models.Site.objects.get(site__exact=site)

        kwargs = dict([(smart_str(k,'ascii'), v.resolve(context))
            for k, v in self.kwargs.items()])
        is_external = False
        for k, v in kwargs.items():
            if k == "is_external":
                is_external = v
                del kwargs[k]
                break
          
        url = mh_reverse(view, site, is_external, args, kwargs)

        if self.as_var:
            context[self.as_var] = url
            return ''
        else:
            return url        
#class MHReverseNode

__kwarg_re = re.compile(r"(?:(\w+)=)?(.+)")


def mh_reverse_tag(parser, token):
    bits = token.split_contents()
    if len(bits) < 3:
        raise TemplateSyntaxError("'%s' takes at least two argument"
                                  " (path to a view) (site)" % bits[0])
    viewname = parser.compile_filter(bits[1])
    site = bits[2]
    if site.startswith('site='):
        site = site[5:]
    if site.startswith('\'') or site.startswith('"'):
        site = site[1:-1]
    else:
        site = parser.compile_filter(site)
    args = []
    kwargs = {}
    as_var = None
    bits = bits[3:]
    if len(bits) >= 3 and bits[-2] == 'as':
        as_var = bits[-1]
        bits = bits[:-2]

    # Backwards compatibility: check for the old comma separated format
    # {% url urlname arg1,arg2 %}
    # Initial check - that the first space separated bit has a comma in it
    if bits and ',' in bits[0]:
        check_old_format = True
        # In order to *really* be old format, there must be a comma
        # in *every* space separated bit, except the last.
        for bit in bits[1:-1]:
            if ',' not in bit:
                # No comma in this bit. Either the comma we found
                # in bit 1 was a false positive (e.g., comma in a string),
                # or there is a syntax problem with missing commas
                check_old_format = False
                break
    else:
        # No comma found - must be new format.
        check_old_format = False

    if check_old_format:
        # Confirm that this is old format by trying to parse the first
        # argument. An exception will be raised if the comma is
        # unexpected (i.e. outside of a static string).
        match = __kwarg_re.match(bits[0])
        if match:
            value = match.groups()[1]
            try:
                parser.compile_filter(value)
            except TemplateSyntaxError:
                bits = ''.join(bits).split(',')

    # Now all the bits are parsed into new format,
    # process them as template vars
    if len(bits):
        for bit in bits:
            match = __kwarg_re.match(bit)
            if not match:
                raise TemplateSyntaxError("Malformed arguments to url tag")
            name, value = match.groups()
            if name:
                kwargs[name] = parser.compile_filter(value)
            else:
                args.append(parser.compile_filter(value))

    return MHReverseNode(viewname, site, args, kwargs, as_var)

register = template.Library()
register.tag(compile_function=mh_reverse_tag, name='mh_reverse')
