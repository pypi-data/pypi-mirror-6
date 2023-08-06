from cratis.app.core.common.templatetags.model_trans import localize

__author__ = 'Alex'


from django.core.urlresolvers import reverse
#from cratis.app.ecommerce.shopping_cart.cart import Cart

from django import template
register = template.Library()

@register.simple_tag()
def category_url(category):
    category_slug = localize(category, 'slug')
    if category_slug != '':
        return reverse('products_in_category_by_slug', kwargs={'category_slug': category_slug})
    else:
        return reverse('products_in_category', kwargs={'category_id': category.pk})

#@register.filter
#def shoping_cart(request):
#    return Cart(request)

@register.simple_tag()
def product_url(product, category=None):

    if not category and product.categories.count():
        category = product.categories.all()[0]

    product_slug = localize(product, 'slug')

    if not category:
        if product_slug != '':
            return reverse('product_by_slug', kwargs={'slug': product_slug})
        else:
            return reverse('product', kwargs={'pk': product.pk})

    else:
        category_slug = localize(category, 'slug')

        if category_slug != '' and product_slug != '':
            return reverse('product_with_cat_both_by_slug',
                kwargs={'slug': product_slug, 'category_slug': category_slug})

        elif category_slug != '':
            return reverse('product_with_cat_cat_by_slug_prod_by_id',
                kwargs={'pk': product.pk, 'category_slug': category_slug})

        elif product_slug != '':
            return reverse('product_with_cat_cat_by_id_prod_by_slug',
                kwargs={'slug': product_slug, 'category_id': category.pk})

        else:
            return reverse('product_with_cat',
                kwargs={'pk': product.pk, 'category_id': category.pk})


