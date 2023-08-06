from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.db.models.fields import DateTimeField
from django import forms
from filer.fields.image import FilerImageField
from voluptuous import MultipleInvalid
import yaml

from .fields import YamlFancyField
from cratis.app.i18n.translate import TranslatableModelMixin
from cratis.app.ecommerce.payment.methods import get_payment_method_selection, get_payment_method
from django.utils.translation import ugettext_lazy as _

class PaymentLog(models.Model):
    date_created = DateTimeField(auto_now_add=True)
    date_updated = DateTimeField(auto_now=True)

    module = models.CharField(max_length=50, null=True, blank=True, default='')
    user_id = models.CharField(max_length=50, null=True, blank=True, default='')
    user_ip = models.CharField(max_length=50, null=True, blank=True, default='')
    operation = models.CharField(max_length=255, null=True, blank=True, default='')
    url = models.CharField(max_length=255, null=True, blank=True, default='')
    request_get = models.TextField(blank=True, null=True, default='')
    request_post = models.TextField(blank=True, null=True, default='')
    data = models.TextField(blank=True, null=True, default='')


class PaymentMethodTranslation(models.Model):
    lang = models.CharField(max_length=2, editable=False)
    name = models.CharField(max_length=150, null=True, blank=True)
    description = models.TextField(blank=True, null=True, default='')

    related = models.ForeignKey('PaymentMethod', null=True, related_name='translations')

class PaymentMethodKey(models.Model):
    name = models.CharField(max_length=150, null=True)
    payment = models.ForeignKey('PaymentMethod', related_name='keys')
    body = models.TextField(blank=True, null=True, default='')

    class Meta:
        unique_together = (("name", "payment"),)

slug_validator = RegexValidator(regex='^[^\d/][^/]+$',
                                message=_('Slug should not start with digit and contain "/" character'))

class PaymentMethod(TranslatableModelMixin, models.Model):
    method = models.CharField(max_length=20, choices=get_payment_method_selection(), null=True)
    enabled = models.BooleanField(default=False, verbose_name=_('Enabled'))

    slug = models.CharField(max_length=255, verbose_name=_('slug'), default='', blank=True, validators=[slug_validator])

    logo = FilerImageField(null=True, blank=True, related_name='payment_method_logo')
    picture = FilerImageField(null=True, blank=True, related_name='payment_method_picture')
    name = models.CharField(max_length=150, null=True)
    description = models.TextField(blank=True, default='')

    sorting = models.PositiveIntegerField(default=0)

    config = YamlFancyField(blank=True, null=True)

    def clean(self):
        try:
            method = self.behavior()
        except yaml.MarkedYAMLError as e:
            raise ValidationError('Config yaml parse error: ' + str(e))
        except MultipleInvalid as e:
            raise ValidationError('Config is not valid: ' + str(e))
        if not method:
            raise ValidationError('Payment method is incorrect.')

    def behavior(self):
        if not self.method:
            return None
        return get_payment_method(self.method, self.parse_config(), self.get_keys())

    def parse_config(self):
        return yaml.load(self.config)

    def get_keys(self):
        return dict([(x.name, x.body) for x in self.keys.all()])

    def __unicode__(self):
        return self.name

    @staticmethod
    def get_translation_class():
        return PaymentMethodTranslation

    class Meta:
        ordering = ('sorting', )