from voluptuous import Schema
from cratis.app.ecommerce.payment.common import Payment

__author__ = 'alex'


class PaymentPaypal(Payment):

    actions_template = 'payment/paypal_actions.html'

    def schema(self):
        #TEST = settings.PAYPAL_TEST
        #USER = settings.PAYPAL_WPP_USER
        #PASSWORD = settings.PAYPAL_WPP_PASSWORD
        #SIGNATURE = settings.PAYPAL_WPP_SIGNATURE

        return Schema({
            'USER': str,
            'PASSWORD': str,
            'SIGNATURE': str,
            'TEST': bool,
        })

    def require_payment(self):
        return True