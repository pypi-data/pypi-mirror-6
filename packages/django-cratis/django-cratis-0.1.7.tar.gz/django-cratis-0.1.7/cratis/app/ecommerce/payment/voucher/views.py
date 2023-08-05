import hashlib
import json
import re
import time

from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.template import RequestContext

from cratis.app.ecommerce.orders.models import Order
from cratis.app.ecommerce.payment.common import log_payment
from cratis.app.ecommerce.payment.views import PaymentView


class VoucherStart(PaymentView):

    def post(self, request, *args, **kwargs):

        method = self.load_method(kwargs['method'])

        log_payment(request, 'voucher_' + kwargs['method'], 'pay_callback')

        order = Order.objects.get(pk=request.session['order_id'])
        order.comment = 'Voucher: %s phone: %s email: %s' % (request.POST['voucher_code'], request.POST['phone'], request.POST['email'])
        order.mark_confirmed()

        return HttpResponseRedirect(reverse('cratis.app.ecommerce.orders.views.confirm'))


