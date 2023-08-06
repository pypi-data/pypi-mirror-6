#!/usr/bin/python
from django.conf import settings

from django.contrib import admin

#from apiclient.discovery import build
from django.contrib.admin.options import InlineModelAdmin

class TranslatableModelMixin(object):

    def translation_list(self):

        if not hasattr(self, 'translations'):
            return {}

        has_trans = []
        for trans in self.translations.all():
            has_trans.append(trans.lang)

        return ', '.join(has_trans)

    translation_list.short_description = 'Translated languages'

class InlineTranslations(admin.StackedInline):
    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

class TranslatableAdmin(admin.ModelAdmin):
    init_translations = []
    translation_class = None

    def save_model(self, request, obj, form, change):
        super(TranslatableAdmin, self).save_model(request, obj, form, change)
        self.fix_translations(obj)

    def fix_translations(self, obj):

        if not self.translation_class:
            return

        if not hasattr(obj, 'translations'):
            return

        has_trans = {}
        for trans in obj.translations.all():
            has_trans[trans.lang] = True

        for (lang, lang_name) in settings.LANGUAGES:
            if lang != settings.MAIN_LANGUAGE and not has_trans.has_key(lang):

                fields = {'lang': lang}

                for field_name in self.init_translations:
                    fields[field_name] = translate(getattr(obj, field_name), settings.MAIN_LANGUAGE, lang)

                obj.translations.add(self.translation_class(**fields))

    def get_object(self, request, object_id):
        obj = super(TranslatableAdmin, self).get_object(request, object_id)

        self.fix_translations(obj)

        return obj

class TranslationError(Exception):
    pass

def translate(message, lang_from, lang_to):

    if lang_to not in _languages:
        raise TranslationError, "Language %s is not supported as lang_to." % lang_to
    if lang_from not in _languages and lang_from != '':
        raise TranslationError, "Language %s is not supported as lang_from." % lang_from

    #try:
    #    service = build('translate', 'v2',
    #                    developerKey='AIzaSyBUKnwQMI3r2pIdSxBAjUjmmrKHoHo1q4s')
    #    data = service.translations().list(
    #        source=lang_from,
    #        target=lang_to,
    #        q=[message]
    #    ).execute()
    #
    #    return data['translations'][0]['translatedText']
    #
    #except Exception, e:
    return None



    # detect_url = "http://ajax.googleapis.com/ajax/services/language/detect?v=1.0&q=%(message)s"

_languages = {
  'af': 'Afrikaans',
  'sq': 'Albanian',
  'am': 'Amharic',
  'ar': 'Arabic',
  'hy': 'Armenian',
  'az': 'Azerbaijani',
  'eu': 'Basque',
  'be': 'Belarusian',
  'bn': 'Bengali',
  'bh': 'Bihari',
  'bg': 'Bulgarian',
  'my': 'Burmese',
  'ca': 'Catalan',
  'chr': 'Cherokee',
  'zh': 'Chinese',
  'zh-CN': 'Chinese_simplified',
  'zh-TW': 'Chinese_traditional',
  'hr': 'Croatian',
  'cs': 'Czech',
  'da': 'Danish',
  'dv': 'Dhivehi',
  'nl': 'Dutch',
  'en': 'English',
  'eo': 'Esperanto',
  'et': 'Estonian',
  'fl': 'Filipino',
  'fi': 'Finnish',
  'fr': 'French',
  'gl': 'Galician',
  'ka': 'Georgian',
  'de': 'German',
  'el': 'Greek',
  'gn': 'Guarani',
  'gu': 'Gujarati',
  'iw': 'Hebrew',
  'hi': 'Hindi',
  'hu': 'Hungarian',
  'is': 'Icelandic',
  'id': 'Indonesian',
  'iu': 'Inuktitut',
  'ga': 'Irish',
  'it': 'Italian',
  'ja': 'Japanese',
  'kn': 'Kannada',
  'kk': 'Kazakh',
  'km': 'Khmer',
  'ko': 'Korean',
  'ku': 'Kurdish',
  'ky': 'Kyrgyz',
  'lo': 'Laothian',
  'lv': 'Latvian',
  'lt': 'Lithuanian',
  'mk': 'Macedonian',
  'ms': 'Malay',
  'ml': 'Malayalam',
  'mt': 'Maltese',
  'mr': 'Marathi',
  'mn': 'Mongolian',
  'ne': 'Nepali',
  'no': 'Norwegian',
  'or': 'Oriya',
  'ps': 'Pashto',
  'fa': 'Persian',
  'pl': 'Polish',
  'pt-PT': 'Portuguese',
  'pa': 'Punjabi',
  'ro': 'Romanian',
  'ru': 'Russian',
  'sa': 'Sanskrit',
  'sr': 'Serbian',
  'sd': 'Sindhi',
  'si': 'Sinhalese',
  'sk': 'Slovak',
  'sl': 'Slovenian',
  'es': 'Spanish',
  'sw': 'Swahili',
  'sv': 'Swedish',
  'tg': 'Tajik',
  'ta': 'Tamil',
  'tl': 'Tagalog',
  'te': 'Telugu',
  'th': 'Thai',
  'bo': 'Tibetan',
  'tr': 'Turkish',
  'uk': 'Ukrainian',
  'ur': 'Urdu',
  'uz': 'Uzbek',
  'ug': 'Uighur',
  'vi': 'Vietnamese',
  'cy': 'Welsh',
  'yi': 'Yiddish'
};

