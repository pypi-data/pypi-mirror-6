import datetime
from decimal import Decimal
import models
from cratis.app.core.settings import SHOP_DELIVERY_PER_PRODUCT
from cratis.app.core.common.templatetags.model_trans import localize

CART_ID = 'CART-ID'


class ItemAlreadyExists(Exception):
    pass


class ItemDoesNotExist(Exception):
    pass


class Cart:
    def __init__(self, request, cart=None):

        if cart:
            self.cart = cart
        else:

            cart_id = request.session.get(CART_ID)

            if not cart_id:
                cart_id = request.get_signed_cookie('cart_id', salt='cart_cart', default=None)

            if cart_id:
                try:
                    cart = models.Cart.objects.get(id=cart_id, checked_out=False)
                except models.Cart.DoesNotExist:
                    cart = self.new(request)
            else:
                cart = self.new(request)
            self.cart = cart

    def __len__(self):
        return len(self.cart.items.all())

    def __iter__(self):
        for item in self.cart.items.all():
            yield item

    def new(self, request):

        cart = models.Cart(creation_date=datetime.datetime.now())
        cart.save()
        request.session[CART_ID] = cart.id
        return cart

    def in_cart(self, item_id):
        if self.is_empty():
            return False

        for item in self.cart.items.all():
            if item.object_id == item_id:
                return True

        return False

    #    def is_locked(self):
    #        return self.cart.order.status != orders.models.Order.ORDER_STATUS_NEW

    def is_empty(self):
        return len(self.cart.items.all()) < 1

    def info(self):
        items = self.cart.items.all()

        total = 0
        sum = Decimal(0)
        for item in items:
            total += item.quantity
            sum += item.total_price

        return {
            'items': [
                {
                    'id': item.product.id,
                    'title': localize(item.product, 'title'),
                    'qty': item.quantity,
                    'delivery_method': item.delivery_method,
                    'price_total': "%01.2f" % item.total_price,
                    'price_unit': "%01.2f" % item.unit_price
                } for item in items],
            'size': len(items),
            'total_elements': total,
            'without_tax': self.cart.without_tax,
            'tax': self.cart.tax,
            'tax_formated': "%01.2f" % (float(sum) * 0.25),
            'total_price_raw': sum,
            'total_price': "%01.2f" % sum
        }


    def set_delivery(self, product, delivery_method):
        try:
            item = models.Item.objects.get(
                cart=self.cart,
                product=product,
            )
        except models.Item.DoesNotExist:
            raise ItemDoesNotExist
        else:
            item.delivery_method = delivery_method
            item.save()

    def set_qty(self, product, quantity):
        try:
            item = models.Item.objects.get(
                cart=self.cart,
                product=product,
            )
        except models.Item.DoesNotExist:
            raise ItemDoesNotExist
        else:
            item.quantity = long(quantity)
            item.save()

    def add(self, product, unit_price, quantity=1):
        try:
            item = models.Item.objects.get(
                cart=self.cart,
                product=product,
            )
        except models.Item.DoesNotExist:
            item = models.Item()
            item.cart = self.cart
            item.product = product

            # select best price
            if product.price_discount and 0 < product.price_discount < product.price:
                item.unit_price = product.price_discount  # unit_price
            else:
                item.unit_price = product.price  # unit_price

            item.quantity = quantity

            if SHOP_DELIVERY_PER_PRODUCT:
                methods = models.DeliveryMethod.objects.filter(enabled=True)
                if len(methods) > 1:
                    item.delivery_method = methods[0]

            item.save()
        else:
            item.quantity += long(quantity)
            item.save()

    def remove(self, product, quantity=0):

        quantity = long(quantity)
        try:
            item = models.Item.objects.get(
                cart=self.cart,
                product=product,
            )
        except models.Item.DoesNotExist:
            raise ItemDoesNotExist
        else:
            print quantity
            if quantity:
                item.quantity -= long(quantity)
                if item.quantity < 1:
                    item.delete()
                else:
                    item.save()
            else:
                item.delete()

    def update(self, product, quantity, unit_price=None):
        try:
            item = models.Item.objects.get(
                cart=self.cart,
                product=product,
            )
        except models.Item.DoesNotExist:
            raise ItemDoesNotExist

    def clear(self):
        for item in self.cart.items.all():
            item.delete()



