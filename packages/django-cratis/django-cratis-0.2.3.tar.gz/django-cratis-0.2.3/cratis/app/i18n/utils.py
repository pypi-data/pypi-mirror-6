

import re
from django.core.exceptions import ObjectDoesNotExist
from django.utils.functional import lazy
from django.conf import settings

from django.utils import translation

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _, get_language, ugettext
from django.utils.text import capfirst
from django.db.models.base import ModelBase


def localize_pattern(text):
    """
    Generates proper prefixse for urls and
    transletes the rest.

    Wrap route with this function if you need translatable url.

    @param text:
    @return:
    """

    translated = ugettext(text)
    language = get_language()

    if language != settings.MAIN_LANGUAGE:
        result = '^' + language + '/' + translated[1:]
    else:
        result = translated

#    print "[%s : %s] : %s {%s}" % (language, settings.MAIN_LANGUAGE, text, result, )
    return result

localize_url = lazy(localize_pattern, unicode)


class I18nLabel():
    def __init__(self, function):
        self.target = function
        self.app_label = u''

    def rename(self, f, name = u''):
        def wrapper(*args, **kwargs):
            extra_context = kwargs.get('extra_context', {})
            if 'delete_view' != f.__name__:
                extra_context['title'] = self.get_title_by_name(f.__name__, args[1], name)
            else:
                extra_context['object_name'] = name.lower()
            kwargs['extra_context'] = extra_context
            return f(*args, **kwargs)
        return wrapper

    def get_title_by_name(self, name, request={}, obj_name = u''):
        if 'add_view' == name:
            return _('Add %s') % obj_name
        elif 'change_view' == name:
            return _('Change %s') % obj_name
        elif 'changelist_view' == name:
            if 'pop' in request.GET:
                title = _('Select %s')
            else:
                title = _('Select %s to change')
            return title % obj_name
        else:
            return ''

    def wrapper_register(self, model_or_iterable, admin_class=None, **option):
        if isinstance(model_or_iterable, ModelBase):
            model_or_iterable = [model_or_iterable]
        for model in model_or_iterable:
            if admin_class is None:
                admin_class = type(model.__name__+'Admin', (admin.ModelAdmin,), {})
            self.app_label = model._meta.app_label
            current_name = model._meta.verbose_name.upper()
            admin_class.add_view = self.rename(admin_class.add_view, current_name)
            admin_class.change_view = self.rename(admin_class.change_view, current_name)
            admin_class.changelist_view = self.rename(admin_class.changelist_view, current_name)
            admin_class.delete_view = self.rename(admin_class.delete_view, current_name)
        return self.target(model, admin_class, **option)

    def wrapper_app_index(self, request, app_label, extra_context=None):
        if extra_context is None:
                extra_context = {}
        extra_context['title'] = _('%s administration') % _(capfirst(app_label))
        return self.target(request, app_label, extra_context)

    def register(self):
        return self.wrapper_register

    def index(self):
        return self.wrapper_app_index


def message_wrapper(f):
    def wrapper(self, request, message):

        return f(self, request, message)

    return wrapper


def _try_to_find_by_localized_field(subject_class, trans_class, lang, args):
    try:
        if lang == settings.MAIN_LANGUAGE:
            return subject_class.objects.get(**args)
        else:
            args['lang'] = lang
            return trans_class.objects.get(**args).related
    except ObjectDoesNotExist:
        return None


def find_by_localized_field(subject_class, field_name, field_value, lang=None):
    args = {field_name: field_value}

    if not lang:
        lang = get_language()

    trans_class = subject_class.get_translation_class()
    result = _try_to_find_by_localized_field(subject_class, trans_class, lang, args)

    if result:
        return result

    # try another languages
    for code, name in settings.LANGUAGES:
        if lang != code: # already tried
            result = _try_to_find_by_localized_field(subject_class, trans_class, code, {field_name: field_value})
            if result:
                return result

    return None
