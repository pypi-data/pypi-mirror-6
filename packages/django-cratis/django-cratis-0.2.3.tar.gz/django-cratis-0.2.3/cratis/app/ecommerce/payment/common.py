import re
from voluptuous import Schema, Invalid

__author__ = 'alex'


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


class NotImplemented(Exception):
    pass


class Payment(object):

    actions_template = None

    def __init__(self, config, keys):
        self.keys = keys
        self.apply_config(config)

        super(Payment, self).__init__()

    def actions_template_name(self):
        return self.actions_template

    def actions_context(self):
        return {}

    def valid_key(self):

        def key_validator(val):
            if len(val) and val[0] == '$':
                val = val[1:]
                if not val in self.keys:
                    raise Invalid('No such key %s' % val)
                return self.keys[val]
            else:
                raise Invalid('Key field must contain reference to a key: %s' % val)

        return key_validator

    def schema(self):
        return Schema({})


    def apply_config(self, config):
        if config:
            schema = self.schema()
            self.config = schema(config)

    def require_payment(self):
        return False




def log_payment(request, module, operation, data=None):
    from cratis.app.ecommerce.payment.models import PaymentLog
    rec = PaymentLog()
    rec.module = module
    rec.operation = operation
    rec.url = request.path

    if not request.user.is_anonymous():
        rec.user_id = request.user.pk

    rec.user_ip = get_client_ip(request)
    rec.request_get = str(request.GET)
    rec.request_post = str(request.POST)

    if data:
        rec.data = str(data)

    rec.save()