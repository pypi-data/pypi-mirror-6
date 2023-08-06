from django.forms.models import ModelForm
from cratis.app.ecommerce.orders.models import  Address

__author__ = 'Alex'

class DeliveryAddressForm(ModelForm):

    class Meta:
        model = Address
        fields = ('city', 'recipient')