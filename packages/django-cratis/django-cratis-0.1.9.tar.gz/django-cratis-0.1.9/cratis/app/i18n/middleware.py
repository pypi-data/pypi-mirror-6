from django.conf import settings
import re
from django.utils import translation


class LocaleRewriteMiddleware(object):
    """
    settings should contain MAIN_LANGUAGE definition.
    """

    def process_response(self, request, response):
        if request.path[0:17] == '/admin/auth/user/':
            response.set_cookie('ad_lang', '1', 60 * 60 * 24 * 365)
        return response

    def process_request(self, request):
        if request.path[0:7] == '/admin/':
            lang = settings.ADMIN_LANGUAGE
        else:
            match = re.match('^/([a-z]{2})/', request.path)
            if match:
                lang = match.group(1)
            else:
                lang = settings.MAIN_LANGUAGE

        translation.activate(lang)
        request.LANGUAGE_CODE = translation.get_language()

        return None
