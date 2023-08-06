from voluptuous import Schema
from cratis.app.ecommerce.payment.common import Payment

__author__ = 'alex'



class DibsPayment(Payment):

    actions_template = 'payment/dibs_actions.html'

    def schema(self):
        return Schema({
            'MD51': str,
            'MD52': str,
            'CREDITCHOICES': [str],
            'MERCHANT': str,
            'LIVE': bool,
            'CALLBACK_DOMAIN': str,
            'CURRENCY': str
        }, required=True)


    def require_payment(self):
        return True


