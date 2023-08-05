from voluptuous import Required, Schema
from cratis.app.ecommerce.payment.common import Payment


class PaytrailPayment(Payment):

    actions_template = 'payment/paytrail_actions.html'

    def schema(self):
        return Schema({
            'secret': str,
            'id': str
        }, required=True)

    def require_payment(self):
        return True


