__author__ = 'Alex'

from django.utils.translation import ugettext as _

class UnknownDeliveryMethod(Exception):
    pass

def get_delivery_methods():
    return {
        'post': DeliveryPost()
    }

def get_delivery_method(name):
    methods = get_delivery_methods()
    if name in methods:
        return methods[name]
    else:
        raise UnknownDeliveryMethod()

def get_delivery_method_selection():
    return (
        ('post', _('Post-like delivery to address')),
    )


class NotImplemented(Exception):
    pass

class Delivery(object):

    def get_display_label(self):
        raise NotImplemented

    def require_address(self):
        return False


class DeliveryPost(Delivery):

    def require_address(self):
        return True

