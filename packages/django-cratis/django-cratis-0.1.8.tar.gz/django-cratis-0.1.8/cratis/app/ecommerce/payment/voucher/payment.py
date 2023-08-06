from django import forms
from voluptuous import Required, Schema
from cratis.app.ecommerce.payment.common import Payment
from django.utils.translation import ugettext as _

class VoucherForm(forms.Form):
    voucher_code = forms.CharField(max_length=100, label=_('Voucher code'))
    email = forms.CharField(max_length=100, label=_('Email'))
    phone = forms.CharField(max_length=100, label=_('Phone'))

class VoucherPayment(Payment):

    actions_template = 'payment/voucher_actions.html'

    def get_form(self, data):
        return VoucherForm(data)

    def actions_context(self):

        return {
            'form': self.get_form(None)
        }


    def schema(self):
        return Schema({
            'pkey': self.valid_key(),
            'pubkey': self.valid_key(),
            'account': str,
            'owner': basestring,
            'id': str,
            'url': str
        }, required=True)

    def require_payment(self):
        return True


