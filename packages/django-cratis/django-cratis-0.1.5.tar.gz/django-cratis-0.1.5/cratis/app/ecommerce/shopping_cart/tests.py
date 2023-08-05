from django.test import TestCase
from cratis.app.ecommerce.products.models import Product
from models import Cart, Item
from django.contrib.auth.models import User
import datetime
from decimal import Decimal


class CartAndItemModelsTestCase(TestCase):

    def test_create_cart_at_first_product(self):
        """
        Cart should be created only just before first product is added to it.

        :return:
        """
        carts = Cart.objects.all()
        assert len(carts) == 0

        self.client.get('/')

        carts = Cart.objects.all()
        assert len(carts) == 0

        self.client.get('/')

        product = Product()
        product.title = 'Test'
        product.price = 3.50
        product.save()

        self.client.get('/cart/add/%s/%d' % (product.pk, 1))

        carts = Cart.objects.all()
        assert len(carts) == 1

