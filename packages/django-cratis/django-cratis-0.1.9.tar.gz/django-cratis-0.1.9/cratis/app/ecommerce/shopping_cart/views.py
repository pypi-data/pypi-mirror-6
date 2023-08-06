"""
Views for cart manipulation.
"""

from cratis.app.ecommerce.shopping_cart.cart import Cart

from django.shortcuts import render_to_response
from django.template import RequestContext

from cratis.app.ecommerce.shopping_cart.models import DeliveryMethod
from cratis.app.ecommerce.products.models import Product


def clear_cart(request):
    """
    Clears out all content from cart
    :param request:
    :return:
    """
    cart = Cart(request)
    cart.clear()

    return render_to_response('elements/shoping_cart.html', {'shoping_cart': cart},
                              context_instance=RequestContext(request))


def set_delivery(request, product_id, method):
    """
    Set delivery method for product.
    This method is used in case of separate delivery on each product.

    :param request:
    :param product_id:
    :param method:
    :return:
    """
    product = Product.objects.get(id=product_id)
    cart = Cart(request)
    cart.set_delivery(product, DeliveryMethod.objects.get(pk=method))
    return render_to_response('elements/shoping_cart.html', {'shoping_cart': cart},
                              context_instance=RequestContext(request))


def set_product_qty(request, product_id, quantity):
    """
    Increase or decrease product quantity in cart.

    :param request:
    :param product_id:
    :param quantity:
    :return:
    """
    product = Product.objects.get(id=product_id)
    cart = Cart(request)
    cart.set_qty(product, quantity)

    return render_to_response('elements/shoping_cart.html', {'shoping_cart': cart},
                              context_instance=RequestContext(request))


def add_to_cart(request, product_id, quantity):
    """
    Add product to cart

    :param request:
    :param product_id:
    :param quantity:
    :return:
    """
    product = Product.objects.get(id=product_id)
    product.sold_count += 1
    product.save()
    cart = Cart(request)
    cart.add(product, product.price, quantity)

    response = render_to_response('elements/shoping_cart.html', {'shoping_cart': cart},
                                  context_instance=RequestContext(request))

    response.set_signed_cookie('cart_id', cart.cart.id, salt='cart_cart')

    return response


def remove_from_cart(request, product_id, quantity):
    """
    Reove product from cart.

    :param request:
    :param product_id:
    :param quantity:
    :return:
    """
    product = Product.objects.get(id=product_id)
    cart = Cart(request)
    cart.remove(product, quantity)

    return render_to_response('elements/shoping_cart.html', {'shoping_cart': cart},
                              context_instance=RequestContext(request))

