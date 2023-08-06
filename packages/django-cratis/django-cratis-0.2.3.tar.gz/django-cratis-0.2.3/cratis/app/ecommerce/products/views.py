from copy import copy
from math import floor, log10, ceil
from random import shuffle, sample
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.db.models.aggregates import Min, Max
import re
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage, InvalidPage
from django.http import HttpResponse, Http404
from django.template.context import RequestContext
from django.utils.translation import get_language, activate
from django.views.decorators.cache import cache_page
from django.views.decorators.http import require_POST
from cratis.app.i18n.utils import find_by_localized_field
from django.shortcuts import render_to_response, redirect
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from cratis.app.i18n.translate import translate

from cratis.app.ecommerce.profile.views import WithShopingCartMixin, WithSidebarMixin
from models import Product
from cratis.app.ecommerce.orders.models import Order, DeliveryMethod
from cratis.app.ecommerce.products.models import ProductAttribute, ProductAttributeType
from django.utils.translation import ugettext as _
from cratis.app.core.common.templatetags.model_trans import localize
from cratis.app.ecommerce.products.templatetags.product_utils import product_url, category_url

from django.contrib.auth import login as auth_login, login
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.tokens import default_token_generator


# from haystack.query import SearchQuerySet

class SearchListView(WithShopingCartMixin, WithSidebarMixin, TemplateView):
    model = Product
    template_name = 'search.html'
    context_object_name = 'products'

    def get_filter_attributes(self, context):

        if context.has_key('cur_category'):
            filters = context['cur_category'].get_own_and_parents_filters()
        else:
            filters = []

        filtered_attributes = {}
        for filter in filters:
            for attr in filter.attributes.all():
                filtered_attributes[attr.pk] = attr

        return filtered_attributes.values()

    def transform_range(self, range, all_char='*'):
        start = range['from'] if range.has_key('from') else all_char
        end = range['to'] if range.has_key('to') else all_char
        return end, start

    def range_to_query(self, range):
        end, start = self.transform_range(range)
        return '[%s TO %s]' % (start, end)

    def update_ranges(self, ranges, data):
        end, start = self.transform_range(data)
        for idx, range in enumerate(ranges):
            r_end, r_start = self.transform_range(range)
            if r_end == end and start == r_start:
                ranges[idx]['cnt'] = data['total_count']

    def calculate_price_ranges(self):

        query = self.calculate_base_query()

        if len(query.all()) < 1:
            return []

        max_value = query.order_by('-price').best_match().price
        min_value = query.order_by('price').best_match().price

        if min_value == max_value:
            return []

        round_digits = int(floor(log10(max_value - min_value))) - 2
        min_value = int(round(min_value, -round_digits))
        max_value = int(round(max_value, -round_digits))

        range_count = 7

        step = (max_value - min_value) / range_count
        step = int(round(step, - int(floor(log10(step)))))

        if min_value != 0:
            min_value = int(round(min_value, - int(floor(log10(min_value)))))

        price_ranges = []

        for i in range(0, range_count):
            r = {}
            if i != 0:
                r['from'] = min_value + step * i
            if i != (range_count - 1):
                r['to'] = min_value + step * (i + 1)
            price_ranges.append(r)

        return price_ranges

    def prepare_filters(self, context, query):
        all_attributes = self.get_filter_attributes(context)

        query = query.facet('attributes')

        price_ranges = self.calculate_price_ranges()
        if len(price_ranges):
            query = query.query_facet('price_range', {
                "range": {
                    "field": "price",
                    "ranges": price_ranges
                }
            })

        facets = {}
        query_facet_counts = query.facet_counts()

        for idx, value in context['selection'].items():
            if idx == 'price':
                query = query.narrow(
                    u'price:%s' % self.range_to_query(price_ranges[int(context['selection']['price'])]))
            else:
                query = query.narrow(u'attributes:"%s"' % (idx + '_' + value))

        filters = []

        if 'fields' in query_facet_counts:
            for facet in query_facet_counts['fields']['attributes']:
                (value, cnt) = facet
                match = re.match('^(\d+)_(.+)$', value)
                if match:
                    i = int(match.group(1))
                    if not i in facets:
                        facets[i] = {}
                    facets[i][match.group(2)] = cnt

            for attribute in all_attributes:
                if facets.has_key(attribute.pk):
                    filters.append({
                        'attribute': localize(attribute, "name"),
                        'id': attribute.pk,
                        'values': sorted([
                            {
                                'id': val,
                                'selected': True if context['selection'].has_key(u'%s' % attribute.pk) and
                                                    context['selection'][u'%s' % attribute.pk] == val else False,
                                'title': val,
                                'cnt': cnt
                            } for val, cnt in facets[attribute.pk].items()
                        ], key=lambda item: item['title'])
                    })

            if 'price_range' in query_facet_counts['queries']:
            #                for range in query_facet_counts['queries']['price_range']['ranges']:


                for range in query_facet_counts['queries']['price_range']['ranges']:
                    self.update_ranges(price_ranges, range)

                for idx, range in enumerate(price_ranges):
                    range['id'] = idx
                    end, start = self.transform_range(range, '...')
                    range['title'] = '%s - %s' % (start, end)
                    range['selected'] = False

                if context['selection'].has_key('price'):
                    selected_price = int(context['selection']['price'])
                    price_ranges[selected_price]['selected'] = True

                filters.append({
                    'attribute': _('Price'),
                    'id': 'price',
                    'values': price_ranges
                })
        context['filters'] = filters
        return query

    def calculate_base_query(self):
        query = SearchQuerySet()
        if self.request.GET.has_key('q'):
            query = query.filter(content=self.request.GET['q'])
        if 'category_id' in self.kwargs:
            query = query.filter(categories=self.kwargs['category_id'])
        return query

    def get_context_data(self, **kwargs):

        context = super(SearchListView, self).get_context_data(**kwargs)

        query = self.calculate_base_query()

        if self.request.GET.has_key('q'):
            context['q'] = self.request.GET['q']

        context['query'] = query

        if self.request.GET.has_key('sort'):
            sort = self.request.GET['sort']
            if sort == 'discount':
                query = query.order_by('-discount')
            elif sort == 'high':
                query = query.order_by('-price')
            elif sort == 'bestseller':
                query = query.order_by('-sold')
            elif sort == 'offers':
                query = query.filter(featured=True).order_by('-sold')
            else:
                sort = 'low'
                query = query.order_by('price')
        else:
            sort = 'low'
            query = query.order_by('price')
        context['sorting'] = sort

        selection = {}
        for key, val in self.request.GET.items():
            if key[0] == '_':
                key = key[1:]
                selection[key] = val
        context['selection'] = selection

        query = self.prepare_filters(context, query)

        if 'cur_category' in context:
        #            context['filters'] = []

            lang_urls = {}
            cur_lang = get_language()
            for code, name in LANGUAGES:
                activate(code)
                lang_urls[code] = category_url(context['cur_category'])
            activate(cur_lang)

            context['override_lang_urls'] = lang_urls

        results = query.all()

        paginator = Paginator(results, 10)

        page = 1
        if self.request.GET.has_key('page'):
            page = self.request.GET['page']

        try:
            page = paginator.page(page)
        except InvalidPage:
            raise Http404("No such page!")

        context['page'] = page

        context['compare_products'] = generate_compare_data(self.request)

        return context


class MainPageListView(WithShopingCartMixin, WithSidebarMixin, ListView):
    model = Product
    template_name = 'profile.html'
    context_object_name = 'products'

    def get_context_data(self, **kwargs):

        context = super(MainPageListView, self).get_context_data(**kwargs)

        query_set = Product.objects.filter(featured=True, active=True)

        if settings.SHOP_PRODUCTS_HIDE_SOLD:
            query_set = query_set.filter(sold=False)

        featured = query_set[:30]
        if len(featured) > 3:
            context['featured'] = sample(featured, 3)
        else:
            context['featured'] = query_set

        query_set = Product.objects.filter(active=True).order_by('-sold_count')

        if settings.SHOP_PRODUCTS_HIDE_SOLD:
            query_set = query_set.filter(sold=False)

        bought = query_set[:30]
        if len(bought) > 3:
            context['bought'] = sample(bought, 3)
        else:
            context['bought'] = query_set

        context['compare_products'] = generate_compare_data(self.request)

        return context

    def get_queryset(self):
        q = Product.objects.all()

        if settings.SHOP_PRODUCTS_HIDE_SOLD:
            q = q.filter(sold=False)

        paginator = Paginator(q, 10)
        page = self.request.GET.get('page')

        try:
            products = paginator.page(page)
        except PageNotAnInteger:
            products = paginator.page(1)
        except EmptyPage:
            products = paginator.page(paginator.num_pages)

        return products


class ProductView(WithShopingCartMixin, WithSidebarMixin, DetailView):
    model = Product
    template_name = 'product.html'
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super(ProductView, self).get_context_data(**kwargs)

        lang_urls = {}
        cur_lang = get_language()
        for code, name in settings.LANGUAGES:
            activate(code)
            lang_urls[code] = product_url(context['product'],
                                          context['cur_category'] if 'cur_category' in context else None)
        activate(cur_lang)

        context['override_lang_urls'] = lang_urls

        return context

    def get_object(self, queryset=None):

        result = None
        if 'slug' in self.kwargs:
            result = find_by_localized_field(Product, 'slug', self.kwargs['slug'])
            if not result:
                raise Http404(_(u"No Products found matching the query"))
        else:
            result = super(ProductView, self).get_object(queryset)

        if not result or result.archived or not result.active:
            raise Http404(_(u"No Products found matching the query"))

        return result



def generate_compare_data(request):
    compare = request.session.get('compare', [])
    products = Product.objects.filter(id__in=compare)
    return products


def render_compare(request):
    return render_to_response('elements/compare.html', {'compare_products': generate_compare_data(request)},
                              context_instance=RequestContext(request))


def add_to_compare(request, product_id):
    compare = request.session.get('compare', [])
    compare.append(product_id)

    request.session['compare'] = compare
    return render_compare(request)


def clear_compare(request):
    request.session['compare'] = []
    return render_compare(request)


@require_POST
@login_required
def reject_order(request, order_id):
    try:
        order = Order.objects.get(pk=order_id, user=request.user.get_profile())
        if order.status == Order.ORDER_STATUS_CONFIRMED:
            order.status = Order.ORDER_STATUS_REJECTED
            order.save()
        return HttpResponse(json.dumps({'ok': True}), mimetype='application/json')
    except Exception, e:
        return HttpResponse(json.dumps({'ok': False, 'error': e.message}), mimetype='application/json')


@require_POST
@login_required
def repeat_order(request, order_id):
    try:
        from cratis.app.ecommerce.shopping_cart import Cart
        order = Order.objects.get(pk=order_id, user=request.user.get_profile())
        cart = Cart(request)

        for item in order.cart.items.all():
            cart.add(item.product, item.product.price, item.quantity)

        return render_to_response('elements/shoping_cart.html', {'shoping_cart': cart},
                                  context_instance=RequestContext(request))
    except Exception, e:
        return HttpResponse(json.dumps({'ok': False, 'error': e.message}), mimetype='application/json')

@require_POST
def trans(request):
    if request.POST['reverse'] == 'true':
        result = translate(request.POST['message'], request.POST['lang'], MAIN_LANGUAGE)
    else:
        result = translate(request.POST['message'], MAIN_LANGUAGE, request.POST['lang'])

    try:
        return HttpResponse(json.dumps({'ok': True, 'result': result}), mimetype='application/json')
    except Exception, e:
        return HttpResponse(json.dumps({'ok': False, 'error': e.message}), mimetype='application/json')


def attr_type(request, type):
    values = [attr.value for attr in ProductAttribute.objects.filter(type=type) if
              attr.value is not None and len(attr.value) > 0]
    values = list(set(values)) # remove duplicates
    return HttpResponse(json.dumps(values), mimetype='application/json')

@cache_page(60 * 10)
def all_products_xml(request):
    return render_to_response('all_products.html', {'products': Product.objects.filter(active=True)},
                              mimetype='application/xml')

