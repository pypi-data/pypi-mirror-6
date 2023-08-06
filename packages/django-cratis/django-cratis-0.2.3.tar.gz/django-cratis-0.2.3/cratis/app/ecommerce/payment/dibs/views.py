import hashlib
import urllib
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.utils.encoding import smart_str
from django.utils.translation import get_language
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from cratis.app.ecommerce.orders.models import Order
from cratis.app.ecommerce.payment.common import log_payment, get_client_ip
from cratis.app.ecommerce.payment.views import PaymentView


def md5(string):
    return hashlib.md5(string).hexdigest()


def validate_payment(request):

    settings = config_get_group('PAYMENT_DIBS')
    transaction_id = request.POST['transact']
    amount = request.POST['amount']
    currency = request.POST['currency']

    hash_data = '&transact=' + \
        smart_str(transaction_id) + '&amount=' + smart_str(
            amount) + '&currency=' + smart_str(currency)
    md5_key1 = settings['MD51']
    md5_key2 = settings['MD52']

    calculated_authkey = md5(md5_key2 + md5(md5_key1 + hash_data))
    if calculated_authkey != request.POST['authkey']:
        log_payment(request, 'dibs', 'pay_accept_error',
                    'Siganture not valid. Data: ' + hash_data + ' Key: ' + calculated_authkey)
        return False
    return True


class DibsAccept(PaymentView):

    def post(self, request, *args, **kwargs):
        log_payment(request, 'dibs', 'pay_accept')

        # skip validation
        order_id = request.POST['orderid']
        print order_id
        order = Order.objects.get(pk=order_id)
        order.mark_paid()

        return HttpResponseRedirect(reverse('cratis.app.ecommerce.orders.views.confirm'))


        #    if not validate_payment(request):
        #        return HttpResponse('Bad signature. Can not accpet payment.', None, 403)
        #

        #
        #    amount = request.POST['amount']
        #
        #    order = Order.objects.get(order_id)
        #    if (order.get_detalisation()['full_total'] * 100) != amount:
        #        log_payment(request, 'dibs', 'pay_accept_error', 'Order amount do not match: %s not equals %s' % (order.get_detalisation()['full_total'] * 100, amount))

        #    return HttpResponse('pay_accept')


class DibsCancel(PaymentView):

    def post(self, request, *args, **kwargs):
        log_payment(request, 'dibs', 'pay_cancel')

    #    order_id = request.POST['orderid']
    #    order = Order.objects.get(order_id)
    #    order.mark_paid()

        return HttpResponseRedirect(reverse('orders_checkout'))


class DibsCallback(PaymentView):

    def post(self, request, *args, **kwargs):
        log_payment(request, 'dibs', 'pay_callback')

        # skip validation
        order_id = request.POST['orderid']
        order = Order.objects.get(order_id)
        order.mark_paid()

        return HttpResponse('ok')


class DibsStart(PaymentView):

    def get(self, request, *args, **kwargs):

        method = self.load_method(kwargs['method'])
        settings = method.behavior().config

        order = Order.objects.get(pk=request.session['order_id'])
    #    order.mark_confirmed()

        detalisation = order.get_detalisation()

    #    for row in detalisation['rows']:
    #        ulink_order.items.append(UlinkOrderItem(smart_str(row['title']), '', str(row['price'])))

        # Preparing the data that we are sending to DIBS
        # Order total to be sent to DIBS must be an int specified in cents or
        # equivalent.
        order_total = int(detalisation['full_total'] * 100)
        order_id = order.id

        # Create md5 hash to make payment secure:
        md5_key = md5(settings['MD52'] +
                      md5(settings['MD51'] + 'merchant=%s&orderid=%s&currency=%s&amount=%s' % (settings['MERCHANT'], order_id, settings['CURRENCY'], order_total)))

        # Create the cancel and accept url, based on the request to get the host
        # and reverse to get the url.
        #        cancelurl = 'http://' + request.META['HTTP_HOST'] + reverse('satchmo_checkout-step1')
        #        accepturl = 'http://' + request.META['HTTP_HOST'] + reverse('DIBS_satchmo_checkout-success')
        #        callbackurl = 'http://' + request.META['HTTP_HOST'] + reverse('DIBS_satchmo_checkout-step4') + '?order_id=' + str(order.id)
        #
        cancelurl = 'http://' + settings['CALLBACK_DOMAIN'] + reverse(
            'dibs_payment_cancel', kwargs={'method': method.slug})
        accepturl = 'http://' + settings['CALLBACK_DOMAIN'] + reverse(
            'dibs_payment_accept', kwargs={'method': method.slug})
        callbackurl = 'http://' + settings['CALLBACK_DOMAIN'] + reverse(
            'dibs_payment_callback', kwargs={'method': method.slug})

        data = [
            ('merchant', settings['MERCHANT']),
            ('amount', order_total),
            ('currency', settings['CURRENCY']),
            ('orderid', order_id),
            ('accepturl', accepturl),
            ('cancelurl', cancelurl),
            ('callbackurl', callbackurl),
            ('ip', get_client_ip(request)),
            #('uniqueoid', 'yes'),
            ('lang', get_language()),
            ('md5key', md5_key),
            ('calcfee', 'yes'),
            # Currently not implemented in the flex window.
            # ('delivery1', order.ship_addressee),
            # ('delivery2', order.ship_street1),
            # ('delivery3',  order.ship_postal_code + ' ' +  order.ship_city)
            ('capturenow', 'yes'),
        ]

        log_payment(request, 'dibs', 'pay_start', data)

    #    if settings['CAPTURE']:
    #    data.append(('capturenow', 'yes'))

        if not settings['LIVE']:
            data.append(('test', 'yes'))

        send_data = urllib.urlencode(data)

        return HttpResponseRedirect('https://payment.architrade.com/paymentweb/start.action?' + send_data)
