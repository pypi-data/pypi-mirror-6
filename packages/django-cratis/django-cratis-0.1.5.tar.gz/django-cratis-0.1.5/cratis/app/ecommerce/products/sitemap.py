from django.conf import settings
from django.contrib.sites.models import get_current_site
from django.core.paginator import EmptyPage, PageNotAnInteger
from django.http import Http404
from django.template.response import TemplateResponse
from django.utils.translation import activate
from cratis.app.ecommerce.products.models import Product, ProductCategory

__author__ = 'alex'

from django.contrib.sitemaps import Sitemap

class ProductCategorySitemap(Sitemap):
    changefreq = "daily"
    priority = 0.5

    def items(self):
        return ProductCategory.objects.all()

    def lastmod(self, obj):
        return obj.date_updated

class ProductSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.7

    def items(self):
        return Product.objects.filter(active=True, archived=False)

    def lastmod(self, obj):
        return obj.date_updated


def sitemap(request, sitemaps, section=None,
            template_name='sitemap.xml', mimetype='application/xml'):
    req_protocol = 'https' if request.is_secure() else 'http'
    req_site = get_current_site(request)

    if section is not None:
        if section not in sitemaps:
            raise Http404("No sitemap available for section: %r" % section)
        maps = [sitemaps[section]]
    else:
        maps = sitemaps.values()
    page = request.GET.get("p", 1)

    urls = []
    for site in maps:
        try:
            if callable(site):
                site = site()
            for (lang, lang_name) in settings.LANGUAGES:
                activate(lang)
                urls.extend(site.get_urls(page=page, site=req_site,
                    protocol=req_protocol))
        except EmptyPage:
            raise Http404("Page %s empty" % page)
        except PageNotAnInteger:
            raise Http404("No page '%s'" % page)

    return TemplateResponse(request, template_name, {'urlset': urls},
        content_type=mimetype)