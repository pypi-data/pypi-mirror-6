from django.conf import settings
from django.core.urlresolvers import resolve, Resolver404, reverse
from django.utils.translation import get_language, activate



def i18n_context(request):
    """
    @type context: HttpRequest
    """
    all_languages = settings.LANGUAGES
    if len(all_languages) == 1:
        return {}

    if request.path[0:7] == '/admin/':
        return {}

    cur_lang = get_language()
    lang_urls = {}

    try:
        match = resolve(request.path)
    except Resolver404:
        match = None

    switched = False

    for code, name in all_languages:
        if match and match.url_name != 'pages-details-by-slug':
            switched = True
            activate(code)
            rev = reverse(match.url_name, kwargs=match.kwargs)
            lang_urls[code] = rev
        else:
            lang_urls[code] = ('/' if code == settings.MAIN_LANGUAGE else ('/' + code + '/'))

    if switched:
        activate(cur_lang)

    context = {
        'default_language': settings.MAIN_LANGUAGE,
        'lang_urls': lang_urls
    }
    if match:
        context['url_name'] = match.url_name

    return context