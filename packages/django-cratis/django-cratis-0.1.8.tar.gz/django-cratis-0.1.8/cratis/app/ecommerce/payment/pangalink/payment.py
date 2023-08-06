from voluptuous import Required, Schema
from cratis.app.ecommerce.payment.common import Payment


class PangalinkPayment(Payment):

    actions_template = 'payment/pangalink_actions.html'

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


