# -*- coding: utf-8 -*-

from datetime import datetime
from decimal import Decimal, ROUND_DOWN, ROUND_UP
import hashlib
from django.core.validators import validate_email
from django.db import models
from django.db.models.deletion import PROTECT, SET_NULL
from django.db.models.fields import DateTimeField
from cratis.app.ecommerce.payment.models import PaymentMethod
from cratis.app.ecommerce.shopping_cart.models import Cart, Item, DeliveryMethod
from django.utils.translation import ugettext_lazy as _
from django.utils import unittest
from cratis.app.ecommerce.profile.models import UserProfile

from paypal.pro.signals import payment_was_successful

__author__ = 'alex'

def show_me_the_money(sender, **kwargs):
    item = sender
    order_id = item['inv']

    order = Order.objects.get(pk=order_id)
    order.status = Order.ORDER_STATUS_PAID
    order.save()

payment_was_successful.connect(show_me_the_money)

class Address(models.Model):
    street_address = models.CharField(max_length=250, null=False, default="", blank=False)
    city = models.CharField(max_length=250, null=False, default="", blank=False)
    post_index = models.CharField(max_length=250, null=False, default="", blank=False)
    country = models.CharField(max_length=250, null=False, default="", blank=False)
    recipient = models.CharField(max_length=250, null=False, default="", blank=True)
    firstname = models.CharField(max_length=250, null=False, default="", blank=False)
    lastname = models.CharField(max_length=250, null=False, default="", blank=False)
    email = models.CharField(max_length=250, null=False, default="", blank=False, validators=[validate_email])
    phone = models.CharField(max_length=250, null=False, default="", blank=False)

    temporary = models.BooleanField(default=False, blank=True)

    is_main = models.BooleanField(default=False, blank=True, verbose_name=_('Default address'))

    profile = models.ForeignKey(UserProfile, null=True, blank=True, default=None,  related_name='adresses')

    def is_ready(self):
        return self.city and \
               self.street_address and \
               self.post_index and \
               self.lastname and \
               self.firstname and \
               self.email and \
               self.phone

    def __unicode__(self):
        return ', '.join([str(self.country), self.city, str(self.post_index), self.street_address, self.recipient])


class Order(models.Model):
    date_created = DateTimeField(auto_now_add=True)
    date_updated = DateTimeField(auto_now=True)

    cart = models.ForeignKey(Cart, related_name='_cart', null=True, on_delete=PROTECT)
    user = models.ForeignKey(UserProfile, related_name='orders', null=True, blank=True, on_delete=SET_NULL)

    email = models.CharField(max_length=150, null=True)
    phone = models.CharField(max_length=40, null=True)

    invoiceData = models.TextField(blank=True, default='')
    is_sent = models.BooleanField(default=True, verbose_name=_('Invoice has been delivered'))

    ip_address = models.CharField(max_length=40, null=True)

    #delivery method

    is_test = models.BooleanField(default=True, verbose_name=_('Is test payment'))

    comment = models.TextField(blank=True, null=True)

    # status

    ORDER_STATUS_NEW = 'new'
    ORDER_STATUS_CONFIRMED = 'confirmed'
    ORDER_STATUS_PAID = 'shipping'
    ORDER_STATUS_COMPLETED = 'completed'
    ORDER_STATUS_RETURNED = 'returned'
    ORDER_STATUS_REJECTED= 'rejected'

    # status
    ORDER_STATUSES = (
        (ORDER_STATUS_NEW, _('New order')),
        (ORDER_STATUS_CONFIRMED, _('Confirmed, waiting for payment')),
        (ORDER_STATUS_PAID, _('Paid, shipping to customer')),
        (ORDER_STATUS_COMPLETED, _('Paid and delivered')),
        (ORDER_STATUS_RETURNED, _('Returned')),
        (ORDER_STATUS_REJECTED, _('Rejected by user')),
    )

    status = models.CharField(max_length=20, choices=ORDER_STATUSES, default=ORDER_STATUS_NEW)

    payment_status = models.CharField(max_length=10, null=True)
    payment_response = models.TextField(blank=True, null=True)

    delivery_method = models.ForeignKey(DeliveryMethod, null=True, on_delete=PROTECT)
    payment_method = models.ForeignKey(PaymentMethod, null=True, on_delete=PROTECT)

    address = models.ForeignKey(Address, null=True, on_delete=SET_NULL)

    smartpost_box = models.IntegerField(null=True)
    smartpost_box_name = models.TextField(blank=True, null=True)

    def full_price(self):
        return self.get_detalisation()['full_total']

    def item_names(self):
        return ', '.join([item.product.title for item in Item.objects.filter(cart=self.cart)])

    def get_linkhash(self):
        return hashlib.sha224(str(self.date_created) + 'fjdkjl' + str(self.id)).hexdigest()

    def fill_items(self):
        if self.cart:
            self.cart.order = self
            for item in self.cart.items.all():
                item.order = self
                item.save()

    def documents(self):
        return 'Invoice: <a href="%s" target="_blank"><img style="margin-bottom: -8px;" src="/assets/img/pdf_icon.gif" alt=""></a>' % self.invoice_pdf_url() + \
        ' Shipping list: <a href="%s" target="_blank"><img style="margin-bottom: -8px;" src="/assets/img/pdf_icon.gif" alt=""></a>' % self.shipping_list_pdf_url()
    documents.allow_tags = True

    def shipping_list_pdf_url_href(self):
        return '<a href="%s" target="_blank"><img style="margin-bottom: -8px;" src="/assets/img/pdf_icon.gif" alt=""></a>' % self.shipping_list_pdf_url()
    shipping_list_pdf_url_href.allow_tags = True

    def invoice_pdf_url_href(self):
        return '<a href="%s" target="_blank"><img style="margin-bottom: -8px;" src="/assets/img/pdf_icon.gif" alt=""></a>' % self.invoice_pdf_url()
    invoice_pdf_url_href.allow_tags = True

    def invoice_pdf_url(self):
        return 'https://s3.amazonaws.com/maksa-shops-invoice/invoice-%s-%s.pdf' % (
            hashlib.sha256(str(self.pk) + "hoho12").hexdigest(),
            hashlib.sha256(str(self.pk) + "hoho21").hexdigest(),
        )
    def shipping_list_pdf_url(self):
        return 'https://s3.amazonaws.com/maksa-shops-invoice/shipping-list-%s-%s.pdf' % (
            hashlib.sha256(str(self.pk) + "hoho12").hexdigest(),
            hashlib.sha256(str(self.pk) + "hoho21").hexdigest(),
        )


    def is_paid(self):
        return self.status == self.ORDER_STATUS_PAID or self.status == self.ORDER_STATUS_COMPLETED

    def can_pay(self):
        return self.status == self.ORDER_STATUS_NEW or self.status == self.ORDER_STATUS_CONFIRMED

    def mark_paid(self):
        self.status = self.ORDER_STATUS_PAID
        self.save()

    def mark_comleted(self):
        self.status = self.ORDER_STATUS_COMPLETED
        self.save()

    def mark_confirmed(self):
        self.fill_items()
        if self.status == self.ORDER_STATUS_NEW:
            self.status = self.ORDER_STATUS_CONFIRMED
        self.date_created = datetime.now()
        self.save()

#        if SHOP_COUNT_PRODUCTS:
#            for item in self.cart.items.all(): # for products that are only in 1 exemplar
#                item.product.sold = True
#                item.product.save()

    def is_empty(self):
        return len(self.cart.items.all) > 0

    def get_detalisation(self):
        rows = []
        cart_total_price = self.cart.total_price
        discount_ = 0

        rows.append({
            'title': u'Сумаа заказа',
            'price': cart_total_price,
        })
        if self.delivery_method:

            rows.append({
                'title': _('Delivery') + ' - ' + self.delivery_method.name,
                'price': self.delivery_method.delivery_price,
            })
        else:
            rows.append({
                'title': _('no delivery'),
                'price': 0,
            })
        #if self.payment_method and self.payment_method.discount > 0:
        #    discount_ = (cart_total_price * self.payment_method.discount * -1).quantize(Decimal('.01'), rounding=ROUND_UP)
        #    rows.append({
        #        'title': _(u'Discount') + ' - '
        #                 + str((self.payment_method.discount * 100).quantize(Decimal('1.'))) + '%' ,
        #        'price': discount_,
        #    })
#        else:
#            rows.append({
#                'title': _('No discounts'),
#                'price': 0,
#                })

        full_total = Decimal('0.0')
        for row in rows:
            full_total += row['price']

        return {
            'full_total': full_total.quantize(Decimal('.01'), rounding=ROUND_DOWN),
            'rows': rows
        }
    details = property(get_detalisation)

    def __unicode__(self):
        return "Order %s" % self.id

    class Meta:
        verbose_name = _('Order')
        verbose_name_plural = _('Orders')

class OrderTestCase(unittest.TestCase):

    def test_create_default_order(self):

        method1 = DeliveryMethod(name='delivery-pickup', delivery_price=Decimal('1.30'))
        method1.save()

        payment1 = PaymentMethod(name='payment-pangalink', discount=0)
        payment1.save()

        cart = Cart()
        cart.creation_date = datetime.now()
        cart.save()

        order = Order()
        order.status = Order.ORDER_STATUS_NEW
        order.cart = cart
        order.delivery_method = DeliveryMethod.objects.get(name='delivery-pickup')
        order.payment_method = PaymentMethod.objects.get(name='payment-pangalink')
        order.save()

        self.assertIsNotNone(Order.objects.get(pk=order.id).delivery_method)
        self.assertIsNotNone(Order.objects.get(pk=order.id).payment_method)

    def test_details_with_empty_order(self):
        order = Order()
        order.cart = Cart()

        details = order.details

        self.assertEqual(0, details['full_total'])
        self.assertEqual(3, len(details['rows'])) # Order record

    def test_details_with_delivery(self):

        order = Order()
        order.delivery_method = DeliveryMethod()
        order.delivery_method.name = 'mock'
        order.delivery_method.delivery_price = Decimal('2.60')
        order.cart = Cart()

        details = order.details

        self.assertEqual(Decimal('2.60'), details['full_total'])
        self.assertEqual(3, len(details['rows'])) # Order record


    def test_details_with_payment_discount(self):

        order = Order()
        order.delivery_method = DeliveryMethod()
        order.delivery_method.name = 'mock'
        order.delivery_method.delivery_price = Decimal('2.60')

        order.cart = Cart()
        order.cart.creation_date = datetime.now()
        order.cart.save()

        item1 = Item()
        item1.quantity = 2
        item1.unit_price = Decimal('1.10')
        item1.cart = order.cart
        item1.save()

        pm = PaymentMethod()
        pm.name = 'mock'
        pm.discount = Decimal('0.03')

        order.payment_method = pm

        details = order.details

        self.assertEqual(Decimal('4.73'), details['full_total'])
        self.assertEqual(3, len(details['rows'])) # Order record

