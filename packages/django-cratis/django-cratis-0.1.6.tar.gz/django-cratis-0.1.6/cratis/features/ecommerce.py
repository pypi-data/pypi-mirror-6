from django.conf.urls import patterns
from cratis.features import Feature


class WebShop(Feature):
    def configure_settings(self, cls):
        super(WebShop, self).configure_settings(cls)

        self.append_apps(cls, [
            # "cratis.app.ecommerce.shopping_cart",
            # "cratis.app.ecommerce.payment",
            "cratis.app.ecommerce.products",
            # "cratis.app.ecommerce.orders"
        ])

        self.append_template_processor(cls, [
            # "cratis.app.ecommerce.products.context.shop_context",
            # "cratis.app.ecommerce.shopping_cart.context.cart_context",
        ])

    def configure_urls(self, cls, urls):
        super(WebShop, self).configure_urls(cls, urls)

        # urls += patterns('',
            # (r'^$', "cratis.app.ecommerce.shopping_cart.urls"),
            # (r'^$', "cratis.app.ecommerce.shops.urls"),
            # (r'^$', "cratis.app.ecommerce.orders.urls"),
        # )
