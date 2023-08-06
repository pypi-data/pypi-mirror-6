import hashlib
import re
import time

from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render

from cratis.app.ecommerce.orders.models import Order
from cratis.app.ecommerce.payment.common import log_payment
from cratis.app.ecommerce.payment.crypto import ssl_sign, load_pem_private_key, load_pem_public_key, ssl_verify, load_pem_cert_public_key
from cratis.app.ecommerce.payment.views import PaymentView


__author__ = 'alex'

def sha1(string):
    return hashlib.sha1(string).hexdigest()

def md5(string):
    return hashlib.md5(string).hexdigest()


class PangalinkCallback(PaymentView):

    def bad_payment(self, request):
        if 'fail_url' in request.session:
            return HttpResponseRedirect(request.session['fail_url'])
        else:
            return HttpResponseRedirect(reverse('orders_checkout'))

    def post(self, request, *args, **kwargs):

        method = self.load_method(kwargs['method'])
        settings = method.behavior().config

        log_payment(request, 'pangalink_' + kwargs['method'], 'pay_callback')

        if request.POST['VK_SERVICE'] != '1101':
            log_payment(request, 'pangalink', 'pay_cancel')

            return self.bad_payment(request)

        mac_data = ''
        for field in ['VK_SERVICE', 'VK_VERSION', 'VK_SND_ID',
                'VK_REC_ID', 'VK_STAMP', 'VK_T_NO', 'VK_AMOUNT', 'VK_CURR',
                'VK_REC_ACC', 'VK_REC_NAME', 'VK_SND_ACC', 'VK_SND_NAME',
                'VK_REF', 'VK_MSG', 'VK_T_DATE']:
            v = request.POST[field]
            vlen = len(v)
            mac_data += str(vlen).zfill(3) + v

        public_key = load_pem_cert_public_key(settings['pubkey'])

        if ssl_verify(mac_data.encode('utf-8'), request.POST['VK_MAC'].decode('base64'), public_key):

            ecuno = request.POST['VK_STAMP']

            order_id = int(ecuno) - 100000

            log_payment(request, 'pangalink', 'pay_success')

            order = Order.objects.get(pk=order_id)
            order.mark_paid()

            return HttpResponseRedirect(reverse('cratis.app.ecommerce.orders.views.confirm'))

        else:

            print request.POST['VK_MAC']
            #return self.bad_payment(request)



class PangalinkCancel(PaymentView):
    def post(self, request, *args, **kwargs):
        log_payment(request, 'pangalink', 'pay_cancel')

        return HttpResponseRedirect(reverse('orders_checkout'))

class PangalinkStart(PaymentView):

    def get(self, request, *args, **kwargs):

        method = self.load_method(kwargs['method'])
        settings = method.behavior().config

        order = Order.objects.get(pk=request.session['order_id'])

        detalisation = order.get_detalisation()

        order_total = detalisation['full_total']
        order_id = order.id


        oid = settings['id']

        ecuno = str(order_id + 100000)
        eamount = str(order_total)
        feedbackurl = 'http://' + request.META['HTTP_HOST'] + reverse('pangalink_payment_callback',
                                                                      kwargs={'method': method.slug})
        cancelurl = 'http://' + request.META['HTTP_HOST'] + reverse('pangalink_payment_callback',
                                                                      kwargs={'method': method.slug})

        # padding
        feedbackurl = feedbackurl.ljust(128)
        ecuno = ecuno.zfill(12)
        eamount = eamount.zfill(12)

        data = {
            'VK_SERVICE': '1001',
            'VK_VERSION': '008',
            'VK_SND_ID': oid,
            'VK_STAMP': ecuno,
            'VK_AMOUNT': eamount,
            'VK_CURR': 'EUR',
            'VK_ACC': settings['account'],
            'VK_NAME': settings['owner'],
            'VK_REF': '',
            'VK_MSG': 'Order id ' + str(order_id),
            'VK_RETURN': feedbackurl,
            'VK_ENCODING': 'utf-8',
        }

        mac_data = ''
        for field in ['VK_SERVICE', 'VK_VERSION', 'VK_SND_ID',
                'VK_STAMP', 'VK_AMOUNT', 'VK_CURR',
                'VK_ACC', 'VK_NAME', 'VK_REF', 'VK_MSG']:
            v = data[field]
            vlen = len(v)
            mac_data += str(vlen).zfill(3) + v

        signed = ssl_sign(mac_data.encode('utf-8'), load_pem_private_key(settings['pkey']))

        data['VK_MAC'] = re.sub('\s+', '', signed.encode('base64'))

        log_payment(request, 'pangalink', 'pay_start', data)

        return render(request, 'payment/post_redirect.html', {'url': settings['url'], 'fields': data.items()})

        #'https://pangalink.net/banklink/ec?' + send_data
        #return HttpResponseRedirect('?' + send_data)

