from django.conf import settings
from django.utils import translation

__author__ = 'alex'

from django import template

register = template.Library()

@register.filter
def localize_value(str):
    cur_language = translation.get_language()
#    langs = dict(LANGUAGES)
#    langs.keys()
    vals = str.split(';')
    if len(vals) < 2:
        return vals[0]

    if cur_language == settings.MAIN_LANGUAGE:
        return vals[0]
    else:
        return vals[1]



@register.filter
def localize(obj, field_name):
    if not hasattr(obj, field_name):
        return None

    cur_language = translation.get_language()
    if cur_language == settings.MAIN_LANGUAGE:
        return getattr(obj, field_name)

    found = ''
    for trans in obj.translations.all():
        if trans.lang == cur_language:
            found = getattr(trans, field_name)
            break
    if found and len(found.strip()) > 0:
        return found

    if settings.USE_FALLBACK_TRANSLATION:
        return getattr(obj, field_name)
    else:
        return ""