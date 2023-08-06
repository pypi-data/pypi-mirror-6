from cratis.app.ecommerce.payment.common import Payment
from cratis.app.ecommerce.payment.dibs.payment import DibsPayment
from cratis.app.ecommerce.payment.pangalink.payment import PangalinkPayment
from cratis.app.ecommerce.payment.paypal.payment import PaymentPaypal
from cratis.app.ecommerce.payment.kardikeskus.payment import KardikeskusPayment
from cratis.app.ecommerce.payment.paytrail.payment import PaytrailPayment
from cratis.app.ecommerce.payment.voucher.payment import VoucherPayment

__author__ = 'Alex'

from django.utils.translation import ugettext as _


class UnknownDeliveryMethod(Exception):
    pass


def get_payment_methods():
    return {
        'kardikeskus': KardikeskusPayment,
        'pangalink': PangalinkPayment,
        'paypal': PaymentPaypal,
        'paytrail': PaytrailPayment,
        'dibs': DibsPayment,
        'invoice': Invoice,
        'voucher': VoucherPayment,
    }


def get_payment_method(name, config, keys):
    methods = get_payment_methods()
    if name in methods:
        return methods[name](config, keys)
    else:
        raise UnknownDeliveryMethod()


def get_payment_method_selection():
    return (
        ('kardikeskus', _('Kardikeskus payment')),
        ('pangalink', _('Pangalink')),
        ('paytrail', _('Paytrail payment')),
        ('paypal', _('PayPal payment')),
        ('dibs', _('DIBS payment')),
        ('invoice', _('Invoice payment')),
        ('voucher', _('Voucher payment')),
    )


class Invoice(Payment):
    actions_template = 'payment/invoice.html'


