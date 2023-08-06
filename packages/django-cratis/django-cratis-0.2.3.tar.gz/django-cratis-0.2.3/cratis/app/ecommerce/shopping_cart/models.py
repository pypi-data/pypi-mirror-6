from decimal import Decimal
from django.db import models
from django.db.models.deletion import PROTECT
from django.utils.translation import ugettext_lazy as _
from filer.fields.image import FilerImageField
from cratis.app.i18n.translate import TranslatableModelMixin
from cratis import settings
from cratis.app.ecommerce.delivery.methods import get_delivery_method_selection, get_delivery_method
from cratis.app.ecommerce.products.models import Product


class DeliveryMethodTranslation(models.Model):
    lang = models.CharField(max_length=2, editable=False)
    related = models.ForeignKey(
        'DeliveryMethod', null=True, related_name='translations')
    name = models.CharField(max_length=150, blank=True, default='')
    description = models.TextField(blank=True, default='')

    class Meta:
        app_label = 'orders'


class DeliveryMethod(TranslatableModelMixin, models.Model):
    name = models.CharField(max_length=150, unique=True)
    #logo = FilerImageField(null=True, blank=True)
    delivery_price = models.DecimalField(
        max_digits=18, decimal_places=2, verbose_name=_('delivery price'))
    description = models.TextField(blank=True, default='')
    method = models.CharField(
        max_length=20, choices=get_delivery_method_selection(), null=True)
    enabled = models.BooleanField(default=False, verbose_name=_('Enabled'))

    def behavior(self):
        return get_delivery_method(self.method)

    @staticmethod
    def get_translation_class():
        return DeliveryMethodTranslation

    class Meta:
        app_label = 'orders'

    def __unicode__(self):
        return self.name


class Cart(models.Model):
    creation_date = models.DateTimeField(verbose_name=_('creation date'))
    checked_out = models.BooleanField(
        default=False, verbose_name=_('checked out'))

    order = models.ForeignKey('orders.Order', null=True, related_name='_cart')

    class Meta:
        verbose_name = _('cart')
        verbose_name_plural = _('carts')
        ordering = ('-creation_date',)

    def __unicode__(self):
        return unicode(self.creation_date)

    def total_price(self):
        items = Item.objects.filter(cart=self)
        total = Decimal('0.0')
        for item in items:
            total += item.total_price
        return total

    total_price = property(total_price)

    def tax(self):
        return Decimal(float(self.total_price) - (float(self.total_price) / (1.0 + float(settings.APP_SETTINGS['tax']) / 100.0)))

    tax = property(tax)

    def without_tax(self):
        return self.total_price - self.tax

    without_tax = property(without_tax)


class Item(models.Model):
    cart = models.ForeignKey(
        Cart, verbose_name=_('cart'), related_name='items')
    quantity = models.PositiveIntegerField(verbose_name=_('quantity'))
    unit_price = models.DecimalField(
        max_digits=18, decimal_places=2, verbose_name=_('unit price'))

    delivery_method = models.ForeignKey(
        DeliveryMethod, null=True, on_delete=PROTECT)

    order = models.ForeignKey('orders.Order', null=True)

    product = models.ForeignKey(Product, null=True, on_delete=PROTECT)

    class Meta:
        verbose_name = _('item')
        verbose_name_plural = _('items')
        ordering = ('cart',)

    def __unicode__(self):
        return u'%d units of %s' % (self.quantity, self.product.__class__.__name__)

    def total_price(self):
        price = self.quantity * self.unit_price

        if self.delivery_method:
            price += self.delivery_method.delivery_price * self.quantity

        return price

    total_price = property(total_price)
