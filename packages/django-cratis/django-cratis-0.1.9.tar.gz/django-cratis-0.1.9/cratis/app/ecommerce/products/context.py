from django.db.models import Count
#from cratis.app.ecommerce.shopping_cart.models import DeliveryMethod
from cratis.app.ecommerce.products.models import ProductCategory

def shop_context(request):
    """
    @type context: HttpRequest
    """

    if request.path[0:7] == '/admin/':
        return {}

    context = {
        'categories': ProductCategory.objects.all(),
        'categories_count': dict([(cat.id, cat.product__count) for cat in ProductCategory.objects.filter(product__active=True).annotate(Count('product'))]),
        # 'delivery_methods': DeliveryMethod.objects.filter(enabled=True)
    }
    return context