import datetime
import urllib
from django import template

register = template.Library()

@register.simple_tag(takes_context=True)
def querystring(context, **kwargs):
    args = context['request'].GET.copy()
    for k, v in kwargs.iteritems():
        args[k] = v
    return args.urlencode()
