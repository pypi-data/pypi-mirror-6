
def cart_context(request):
    """
    @type context: HttpRequest
    """

    if request.path[0:7] == '/admin/':
        return {}

    from cratis.app.ecommerce.shopping_cart.cart import Cart

    context = {
        'shoping_cart': Cart(request)
    }
    return context