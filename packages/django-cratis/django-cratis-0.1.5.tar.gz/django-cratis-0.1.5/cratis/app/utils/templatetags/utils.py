from django.utils.encoding import smart_str
from django.utils.safestring import mark_safe
import re
import locale


__author__ = 'Alex'

from django import template
register = template.Library()


VALID_TAGS = ['strong', 'em', 'p', 'ul', 'li', 'br', 'img']

from cms.models import Page
from cms.templatetags.cms_tags import PageUrl



class PageUrlOr(PageUrl):
    name = 'page'

    def get_context(self, context, page_lookup, lang, site):
        try:
            context = super(PageUrlOr, self).get_context(context, page_lookup, lang, site)
        except Page.DoesNotExist:
            return {'content': '#'}
        return context

register.tag(PageUrlOr)

@register.filter()
def smartstr(val):
    return smart_str(val)

@register.filter()
def is_category_active(node, current):
    return node.id == current.id or (node.parent and node.parent.id == current.id or (node.parent.parent and node.parent.parent.id == current.id))

@register.filter()
def nospaces(value):
    print(value)
    value = re.sub('/\s+/m', ' ', value)
    print value
    return value

@register.filter
def get(d, key):
    return d.get(key)

