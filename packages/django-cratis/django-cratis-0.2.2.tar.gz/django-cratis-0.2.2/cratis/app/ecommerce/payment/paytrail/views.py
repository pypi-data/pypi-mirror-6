from collections import namedtuple, OrderedDict
import hashlib
import time

from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from cratis.app.core.settings import APP_SETTINGS

from cratis.app.ecommerce.orders.models import Order
from cratis.app.ecommerce.payment.common import log_payment
from cratis.app.ecommerce.payment.crypto import ssl_sign, load_pem_private_key, load_pem_public_key, ssl_verify
from cratis.app.ecommerce.payment.views import PaymentView


__author__ = 'alex'


def sha1(string):
    return hashlib.sha1(string).hexdigest()


def md5(string):
    return hashlib.md5(string).hexdigest()


class PaytrailAccept(PaymentView):
    def get(self, request, *args, **kwargs):
        log_payment(request, 'paytrail', 'pay_accept')

        method = self.load_method(kwargs['method'])
        settings = method.behavior().config

        # skip validation
        

        order_id = request.GET['ORDER_NUMBER']
        timestamp = request.GET['TIMESTAMP']
        paid = request.GET['PAID']
        method = request.GET['METHOD']
        authcode = request.GET['RETURN_AUTHCODE']

        mac_data = '|'.join((order_id, timestamp, paid, method, settings['secret']))

        if md5(mac_data).upper() != authcode:
                return HttpResponse('Bad signature. Can not accpet payment.', None, 403)

        order = Order.objects.get(pk=order_id)
        order.mark_paid()

        return HttpResponseRedirect(reverse('cratis.app.ecommerce.orders.views.confirm'))

class PaytrailCancel(PaymentView):
    def post(self, request, *args, **kwargs):
        log_payment(request, 'paytrail', 'pay_cancel')

        #    order_id = request.GET['orderid']
        #    order = Order.objects.get(order_id)
        #    order.mark_paid()

        return HttpResponseRedirect(reverse('orders_checkout'))


class PaytrailCallback(PaymentView):
    def post(self, request, *args, **kwargs):
        log_payment(request, 'paytrail', 'pay_callback')

        # skip validation
        order_id = request.GET['orderid']
        order = Order.objects.get(order_id)
        order.mark_paid()

        return HttpResponse('ok')


class PaytrailStart(PaymentView):
    def get(self, request, *args, **kwargs):
        method = self.load_method(kwargs['method'])
        settings = method.behavior().config

        order = Order.objects.get(pk=request.session['order_id'])

        detalisation = order.get_detalisation()

        order_total = detalisation['full_total']

        data = OrderedDict()
        data['MERCHANT_ID'] = settings['id']
        data['AMOUNT'] = str(order_total)
        data['ORDER_NUMBER'] = str(order.id)
        data['REFERENCE_NUMBER'] = ''
        data['ORDER_DESCRIPTION'] = ''
        data['CURRENCY'] = 'EUR'
        data['RETURN_ADDRESS'] = 'http://' + request.META['HTTP_HOST'] + \
                          reverse('paytrail_payment_accept', kwargs={'method': method.slug})
        data['CANCEL_ADDRESS'] = 'http://' + request.META['HTTP_HOST'] + \
                          reverse('paytrail_payment_cancel', kwargs={'method': method.slug})
        data['PENDING_ADDRESS'] = ''
        data['NOTIFY_ADDRESS'] = 'http://' + request.META['HTTP_HOST'] + \
                          reverse('paytrail_payment_callback', kwargs={'method': method.slug})

        data['TYPE'] = 'S1'
        data['CULTURE'] = 'en_US'
        data['PRESELECTED_METHOD'] = ''
        data['MODE'] = '1'
        data['VISIBLE_METHODS'] = ''
        data['GROUP'] = ''


#6pKF4jkv97zmqBJ3ZL8gUw5DfT2NMQ|13466|99.90|123456||Testitilaus|EUR|http://www.esimerkki.fi/success|http://www.esimerkki.fi/cancel||http://www.esimerkki.fi/notify|S1|fi_FI|1||
#6pKF4jkv97zmqBJ3ZL8gUw5DfT2NMQ|13466|99.90|123456||Testitilaus|EUR|http://www.esimerkki.fi/success|http://www.esimerkki.fi/cancel||http://www.esimerkki.fi/notify|S1|fi_FI||1||

        #
        #data['MERCHANT_ID'] = settings['id']
        #data['AMOUNT'] = '99.90'
        #data['ORDER_NUMBER'] = '123456'
        #data['REFERENCE_NUMBER'] = ''
        #data['ORDER_DESCRIPTION'] = 'Testitilaus'
        #data['CURRENCY'] = 'EUR'
        #data['RETURN_ADDRESS'] = 'http://www.esimerkki.fi/success'
        #data['CANCEL_ADDRESS'] = 'http://www.esimerkki.fi/cancel'
        #data['PENDING_ADDRESS'] = ''
        #data['NOTIFY_ADDRESS'] = 'http://www.esimerkki.fi/notify'
        #
        #data['TYPE'] = 'S1'
        #data['CULTURE'] = 'fi_FI'
        #data['PRESELECTED_METHOD'] = ''
        #data['MODE'] = '1'
        #data['VISIBLE_METHODS'] = ''
        #data['GROUP'] = ''

        mac_data = settings['secret'] + '|' + '|'.join(data.values())

        mac = md5(mac_data).upper()

        data['AUTHCODE'] = mac

        log_payment(request, 'paytrail', 'pay_start', data)

        url = 'https://payment.verkkomaksut.fi/'

        return render(request, 'payment/post_redirect.html', {'url': url, 'fields': data.items()})

