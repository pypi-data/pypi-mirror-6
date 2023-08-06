from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('',
    url(r'^cart/delivery/(?P<product_id>\d+)/(?P<method>[a-zA-Z0-9\-_]+)$', 'cratis.app.ecommerce.shopping_cart.views.set_delivery', name='cart_delivery'),
    url(r'^cart/qty/(?P<product_id>\d+)/(?P<quantity>\d+)$', 'cratis.app.ecommerce.shopping_cart.views.set_product_qty', name='cart_qty'),
    url(r'^cart/add/(?P<product_id>\d+)/(?P<quantity>\d+)$', 'cratis.app.ecommerce.shopping_cart.views.add_to_cart', name='cart_add'),
    url(r'^cart/remove/(?P<product_id>\d+)/(?P<quantity>\d+)$', 'cratis.app.ecommerce.shopping_cart.views.remove_from_cart', name='cart_remove'),
    url(r'^cart/clear$', 'cratis.app.ecommerce.shopping_cart.views.clear_cart', name='cart_clear'),
)
