from voluptuous import Required, Schema
from cratis.app.ecommerce.payment.common import Payment


class KardikeskusPayment(Payment):

    actions_template = 'payment/kardikeskus_actions.html'

    def schema(self):
        return Schema({
            'pkey': self.valid_key(),
            'pubkey': self.valid_key(),
            'id': str,
            'url': str
        }, required=True)

    def require_payment(self):
        return True


