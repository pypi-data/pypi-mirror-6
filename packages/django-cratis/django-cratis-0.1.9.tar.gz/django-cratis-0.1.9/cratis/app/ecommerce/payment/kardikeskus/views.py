import hashlib
import time

from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render

from cratis.app.ecommerce.orders.models import Order
from cratis.app.ecommerce.payment.common import log_payment
from cratis.app.ecommerce.payment.crypto import ssl_sign, load_pem_private_key, load_pem_public_key, ssl_verify
from cratis.app.ecommerce.payment.views import PaymentView


__author__ = 'alex'

def sha1(string):
    return hashlib.sha1(string).hexdigest()

def md5(string):
    return hashlib.md5(string).hexdigest()


class KardikeskusCallback(PaymentView):

    def post(self, request, *args, **kwargs):

        method = self.load_method(kwargs['method'])
        settings = method.behavior().config

        log_payment(request, 'kardikeskus_' + kwargs['method'], 'pay_callback')

        oid = settings['id']

        ecuno = request.POST['ecuno']

        receipt_no = request.POST['receipt_no']
        eamount = request.POST['eamount']
        datetime = request.POST['datetime']
        mac = request.POST['mac'].decode('hex')
        respcode = request.POST['respcode']
        msgdata = request.POST['msgdata']
        actiontext = request.POST['actiontext']
        id = request.POST['id']
        ver = request.POST['ver']
        cur = request.POST['cur']

        #ver = '004'
        #eamount = str(order_total)
        #cur = 'EUR'
        #datetime = time.strftime("%Y%m%d%H%M%S")
        #feedbackurl = 'http://' + request.META['HTTP_HOST'] + reverse('kardikeskus_payment_callback',
        #                                                              kwargs={'method': method.slug})
        #delivery = 'S'
        #
        ## padding
        #feedbackurl = feedbackurl.ljust(128)
        #ecuno = ecuno.zfill(12)
        #eamount = eamount.zfill(12)
        #
        #
        #
        #

        data = ''
        data += ver.zfill(3)
        data += id.ljust(10, ' ')
        data += ecuno.zfill(12)
        data += receipt_no.zfill(6)
        data += eamount.zfill(12)
        data += cur.rjust(3, ' ')
        data += respcode
        data += datetime
        data += unicode(msgdata).ljust(40, ' ')
        data += unicode(actiontext).ljust(40, ' ')


        #sprintf("%03s", $ver) . sprintf("%-10s", "$id") .
#sprintf("%012s", $ecuno) . sprintf("%06s", $receipt_no) . sprintf("%012s",
#$eamount) . sprintf("%3s", $cur) . $respcode . $datetime . mb_sprintf("%-40s",
#$msgdata) . mb_sprintf("%-40s", $actiontext);
#

        #print data
        #print mac
        #data = ver+id+ecuno+receipt_no+eamount+cur+respcode+datetime+msgdata+actiontext

        order_id = int(ecuno) - 100000

        #if ssl_verify(data, mac, load_pem_public_key(settings['pubkey'])):
        #
        #    return HttpResponse('okkkk')
        #else:
        #    return HttpResponse('not ok')


        log_payment(request, 'kardikeskus', 'pay_callback')

        # skip validation
        #order_id = request.POST['orderid']
        order = Order.objects.get(pk=order_id)
        order.mark_paid()

        return HttpResponseRedirect(reverse('cratis.app.ecommerce.orders.views.confirm'))


class KardikeskusStart(PaymentView):

    def get(self, request, *args, **kwargs):

        method = self.load_method(kwargs['method'])
        settings = method.behavior().config

        order = Order.objects.get(pk=request.session['order_id'])

        detalisation = order.get_detalisation()

    #    for row in detalisation['rows']:
    #        ulink_order.items.append(UlinkOrderItem(smart_str(row['title']), '', str(row['price'])))

        order_total = int(detalisation['full_total'] * 100)
        order_id = order.id


    #    key = """

    #"""
    #    oid = 'EB00310653'
        oid = settings['id']

        ecuno = str(order_id + 100000)
        ver = '004'
        eamount = str(order_total)
        cur = 'EUR'
        datetime = time.strftime("%Y%m%d%H%M%S")
        feedbackurl = 'http://' + request.META['HTTP_HOST'] + reverse('kardikeskus_payment_callback',
                                                                      kwargs={'method': method.slug})
        delivery = 'S'

        # padding
        feedbackurl = feedbackurl.ljust(128)
        ecuno = ecuno.zfill(12)
        eamount = eamount.zfill(12)

        data = ver + oid + ecuno + eamount + cur + datetime + feedbackurl + delivery

        signed = ssl_sign(data, load_pem_private_key(settings['pkey']))

        mac = signed.encode('hex')

        data = {
            'lang': 'et', # get_language(),
            'action': 'gaf',
            'ver': ver,
            'id': oid,
            'ecuno': ecuno,
            'eamount': eamount,
            'cur': 'EUR',
            'datetime': datetime,
            'charEncoding': 'UTF-8',
            'feedBackUrl': feedbackurl.strip(),
            'delivery': delivery,
            'mac': mac
        }

        log_payment(request, 'kardikeskus', 'pay_start', data)

        return render(request, 'payment/post_redirect.html', {'url': settings['url'], 'fields': data.items()})

        #'https://pangalink.net/banklink/ec?' + send_data
        #return HttpResponseRedirect('?' + send_data)

