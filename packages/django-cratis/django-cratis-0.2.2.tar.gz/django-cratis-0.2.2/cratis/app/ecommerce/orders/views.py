#coding:utf-8
# Create your views here.
import base64
import json
from smtplib import SMTPRecipientsRefused
import cloud
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.sites.models import Site
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.decorators.csrf import  csrf_exempt
from django.views.decorators.http import require_POST
from django.views.generic.base import TemplateView
from django.utils import translation
from cratis.app.ecommerce.shopping_cart.cart import Cart
from cratis.app.core.common.registration import user_registered_signal
from cratis.app.ecommerce.profile.views import WithShopingCartMixin, WithSidebarMixin, AddressForm
from cratis.app.ecommerce.orders.models import Order, DeliveryMethod, PaymentMethod, Address

from django.utils.translation import ugettext as _
from cratis.app.ecommerce.payment.common import get_client_ip
from cratis.app.core.settings import SHOP_DELIVERY_PER_PRODUCT, APP_SETTINGS, MAIN_LANGUAGE
#from ulink.order import OrderItem as UlinkOrderItem, Order as UlinkOrder
#from ulink.protocol import TransportPacket
#from ulink.request import PaymentRequest, CURRENCY_EURO, create_from_json
#import ulink.utils as CryptoUtils

import logging

from django.contrib.auth.models import User

logger = logging.getLogger('maxe')

import string, random
from cratis.app.core.common.templatetags.model_trans import localize

def generate_password(length):
    password = []

    password_len = length

    for group in (string.ascii_letters, string.digits):
        password += random.sample(group, 3)

    password += random.sample(
        string.ascii_letters + string.punctuation + string.digits,
        password_len - len(password))

    random.shuffle(password)
    return ''.join(password)


@require_POST
def set_delivery(request):
    method = request.POST['method']
    order = Order.objects.get(pk=request.session['order_id'])
    order.delivery_method = DeliveryMethod.objects.get(pk=method)
    order.save()
    return render_to_response('shops/order_details.html', {'details': order.details})

def json_response(response):
    return HttpResponse(json.dumps(response), mimetype='application/javascript')

@require_POST
def validate(request):
    order = Order.objects.get(pk=request.session['order_id'])

    if not order.address:
        return json_response({'ok': False, 'type': 'overall', 'msg': str(_('Address is not selected'))})

    if order.address.temporary:
        address_form = AddressForm(order.address.__dict__, instance=order.address)
        if not address_form.is_valid():
            return json_response({'ok': False, 'type': 'form', 'errors': address_form._errors,
                                  'msg': _('Address is not filled correctly')})

    if not request.user or request.user.is_anonymous():
        result = User.objects.filter(email=order.email)
        if result:
            return json_response({'ok': False, 'type': 'overall', 'msg': _('Email belongs to one of site accounts. Please login to the site to use this email.')})

    return json_response({'ok': True})

@require_POST
def set_payment(request):
    method = request.POST['method']
    order = Order.objects.get(pk=request.session['order_id'])

    #if not request.user or request.user.is_anonymous():
    #    result = User.objects.filter(email=order.email)
    #    if result:
    #        return render_to_response('shops/payment_not_ready.html',
    #                {'details': order.details, 'order': order, 'error': _('Email belongs to one of site accounts. Please login to the site to use this email.')})
    #
    #if not order.address or not order.address.is_ready():
    #    return render_to_response('shops/payment_not_ready.html',
    #        {'details': order.details, 'order': order, 'error': _('You should fill all address fields to continue.')})


    method = PaymentMethod.objects.get(pk=method)
    order.payment_method = method
    order.save()

    return render_to_response('shops/payment_actions.html', {'details': order.details, 'order': order},
                                    context_instance=RequestContext(request))




#@require_POST
#def set_smartpost_box(request):
#    order = Order.objects.get(pk=request.session['order_id'])
#    order.smartpost_box = request.POST['box_id']
#    order.smartpost_box_name = request.POST['box_name']
#    order.save()
#    return HttpResponse(json.dumps({'ok':True}), mimetype='application/javascript')




@require_POST
def update_address(request):
    order = Order.objects.get(pk=request.session['order_id'])

    if 'address_id' in request.POST:
        if order.address and order.address.temporary:
            order.address.delete()

        if request.POST['address_id'] == 0:
            order.address = None
        else:
            try:
                order.address = Address.objects.get(pk=request.POST['address_id'], profile=request.user.get_profile())

                for address in request.user.get_profile().saved_adresses():
                    address.is_main = (order.address.pk == address.pk)
                    address.save()

            except ObjectDoesNotExist:
                order.address = None
        order.save()
    else:
        if not order.address or not order.address.temporary:
            address = Address()
            address.temporary = True
            address.profile = request.user.get_profile() if not request.user.is_anonymous() else None
            address.save()
            order.address = address
            order.save()

        #if 'country' in request.POST:
        #    order.address.country = request.POST['country']
        #order.address.city = request.POST['city']
        #order.address.post_index = request.POST['post_index']
        #order.address.email = request.POST['email']
        #order.address.lastname = request.POST['lastname']
        #order.address.street_address = request.POST['street_address']
        #order.address.firstname = request.POST['firstname']
        #order.address.phone = request.POST['phone']

        address_form = AddressForm(request.POST, instance=order.address)

        if not address_form.is_valid():
            # still save data
            for key, value in request.POST.items():
                setattr(order.address, key, value)
            order.address.save()
            return HttpResponse(json.dumps({'ok': False, 'errors': address_form._errors}), mimetype='application/javascript')
        address_form.save()

    if order.address.email:
        order.email = order.address.email
        order.save()

    return HttpResponse(json.dumps({'ok':True}), mimetype='application/javascript')


@require_POST
def update_contacts(request):
    order = Order.objects.get(pk=request.session['order_id'])

    order.email = request.POST['email']

    order.save()

    return HttpResponse(json.dumps({'ok':True}), mimetype='application/javascript')

class OrderStatusView(WithShopingCartMixin, WithSidebarMixin, TemplateView):
    template_name= 'order_status.html'

    def get_context_data(self, **kwargs):
        context = super(OrderStatusView, self).get_context_data(**kwargs)
        return context

class PaymentWaitView(WithShopingCartMixin, WithSidebarMixin, TemplateView):
    template_name='payment_wait.html'

    def get_context_data(self, **kwargs):
        context = super(PaymentWaitView, self).get_context_data(**kwargs)

        order = Order.objects.get(pk=self.request.session['order_id'])
        context['order'] = order
        context['status'] = order.payment_status if order.payment_status else 'wait'

        return context

class CheckoutDoneView(WithShopingCartMixin, WithSidebarMixin, TemplateView):
    template_name= 'checkout_confirm.html'

    def get_context_data(self, **kwargs):
        context = super(CheckoutDoneView, self).get_context_data(**kwargs)

        context['order'] = Order.objects.get(pk=self.request.session['prev_order_id'])

        return context

class CheckoutView(WithShopingCartMixin, WithSidebarMixin, TemplateView):
    template_name= 'checkout.html'

    def create_new_order(self, request, shopping_cart):
        order = Order()

        if not self.request.user.is_anonymous():
            order.user = self.request.user.get_profile()
            for address in order.user.saved_adresses():
                if address.is_main:
                    order.address = address

        order.status = Order.ORDER_STATUS_NEW
        order.cart = shopping_cart.cart
        if request.session.has_key('prev_order_id'):
            try:
                prev_order = Order.objects.get(pk=request.session['prev_order_id'])

                for field in (
                'email', 'delivery_method', 'payment_method', 'address'):
                    setattr(order, field, getattr(prev_order, field))
            except ObjectDoesNotExist:
                pass

        order.save()
        request.session['order_id'] = order.id

        return order

    def prepare_order(self, request):

        shopping_cart = Cart(request)

        if (not request.session.has_key('order_id')) or request.session['order_id'] is None:
            order = self.create_new_order(request, shopping_cart)
        else:
            try:
                order = Order.objects.get(pk=request.session['order_id'])
            except ObjectDoesNotExist:
                order = self.create_new_order(request, shopping_cart)

        # update order items
        order.fill_items()

        order.ip_address = get_client_ip(request)

        if not order.email and not request.user.is_anonymous():
            order.email = request.user.email
            order.save()

        if not order.user and not request.user.is_anonymous():
            order.user = request.user.get_profile()
            order.save()

        return order

    def get_context_data(self, **kwargs):
        context = super(CheckoutView, self).get_context_data(**kwargs)

        order = self.prepare_order(self.request)

        context['order'] = order

        context['delivery_methods'] = DeliveryMethod.objects.all()
        context['payment_methods'] = PaymentMethod.objects.filter(enabled=True)

        if not self.request.user.is_anonymous():
            context['addresses'] = self.request.user.get_profile().adresses.filter(temporary=False)

        if order.address:
            address_form = AddressForm(instance=order.address)
        else:
            address_form = AddressForm()

        context['address_form'] = address_form

        if len(context['delivery_methods']) == 1:
            order.delivery_method = context['delivery_methods'][0]
            order.save()

        if not order.payment_method and len(context['payment_methods']):
            order.payment_method = context['payment_methods'][0]
            order.save()

        context['need_delivery'] = not SHOP_DELIVERY_PER_PRODUCT

        return context


@require_POST
def payment_check(request):
    order = Order.objects.get(pk=request.session['order_id'])
    return HttpResponse(json.dumps({'status':order.payment_status}), mimetype='application/json')

@require_POST
@csrf_exempt
def payment_response(request):

#    try:
#        rawData = request.POST['signedResponse']
#
#        privateKey = CryptoUtils.load_pem_private_key(ULINK_PRIV_KEY)
#        pubKey = CryptoUtils.load_pem_public_key(ULINK_SERVER_PUB_KEY)
#
#        packet = TransportPacket.create_from_json(rawData)
#        packet.validateAgainstKey(pubKey)
#        decodedPacket = CryptoUtils.unseal(packet.request, privateKey)
#        paymentResponse = create_from_json(smart_unicode(decodedPacket))
#
#        order = Order.objects.get(pk=paymentResponse.clientTransactionId)
#
#        if paymentResponse.isSuccess:
#            order.payment_status = 'success'
#            order.status = Order.ORDER_STATUS_PAID
#        else:
#            order.payment_status = 'failure'
#
#        order.payment_response = smart_unicode(decodedPacket)
#        order.save()
#
#        return HttpResponse(json.dumps({'status':'OK'}), mimetype='application/json')
#
#    except Exception as e:
    return HttpResponse(json.dumps({'status':'NOTOK', 'msg': 'WTF?'}), mimetype='application/json')


def get_url_prefix():
    current_site = Site.objects.get_current()
    prefix = 'http://' + current_site.domain
    return prefix


def get_order_hash_url(order):
    prefix = get_url_prefix()
    order_url = prefix + reverse('orders_status', kwargs={'order_id': order.id, 'hash': order.get_linkhash()})
    return order_url

def add_invoice_delivery_task(order):

    translation.activate(MAIN_LANGUAGE)

    address_post_index = ", " + order.address.post_index if order.address.post_index else ''
    delivery_address = order.address.firstname + ' ' + order.address.lastname + "\n" +\
                       order.address.street_address + "\n" + \
                       order.address.city + address_post_index + ", " + order.address.country + "\n" + \
        "Tel: " + order.address.phone + "\n" + \
        "Email: " + order.email

    rows = []

    for item in order.cart.items.all():
        rows.append({
            'id': item.pk,
            'title': localize(item.product, 'title'),
            'qty': item.quantity,
            'unitPrice': str(item.unit_price),
            'totalPrice': str(item.total_price),
            'deliveryPrice': str(item.delivery_method.delivery_price if item.delivery_method else 0)
        })

    invoice = {
        'id': order.pk,
        'date': str(order.date_created.date()),
        'email': order.email,
        'adminEmail': APP_SETTINGS['invoice']['email'],
        'fromEmail': APP_SETTINGS['invoice']['email'],
        'companyName': _('Inter24 Inc.'),

        'infoHeader':   "",

        'shippingReturnAddress':   _("InterCom Group LTD.\n" +
                        "Inter24\n" +
                        "Parnu mnt 238, 11622\n" +
                        "Tallinn, Harjumaa\n" +
                        "Estonia"),

        'infoFooterCol1': _("Logistikcenter\n" +
                          "InterCom Group AB:\n" +
                          "Parnu mnt. 238\n" +
                          "11622 Tallinn, Estonia\n" +
                          "Reg. 10113432\n" +
                          "Momsnummer SE502071470401"),

        'infoFooterCol2': _("Telefon: (+46) 812 410 605\n" +
                          "E-post: info@inter24.se\n" +
                          "Webbplats: www.inter24.se"),

        'infoFooterCol3': _("Bank: SEB Banken\n" +
                        "Adress: Kungstradgardsg 8,\n" +
                        "10640 Stockholm, Sweden\n" +
                        "Bankkonto: 52771027720\n" +
                        "BankGiro: 737-3459\n" +
                        "IBAN: SE8750000000052771027720\n" +
                        "SWIFT: ESSESESS"),

        'logo': APP_SETTINGS['invoice']['logo'],
	    'billAddress': delivery_address,
        'shippingAddress': delivery_address,
        'subtotal': str(order.cart.without_tax),
        'tax': APP_SETTINGS['tax'],
        'taxTotal': str(order.cart.tax),
        'total': str(order.cart.total_price),

        'rows': rows,

        'texts': {
           'sh_invoice_no': _("INVOICE No. "),
            'sh_invoice_from': _("From:"),
            'sh_invoice_to': _("To:"),
            'invoice_col_id': _("Product ID"),
            'invoice_col_description': _("Description"),
            'invoice_col_delivery': _("Delivery"),
            'invoice_col_quantity': _("Qty"),
            'invoice_col_total': _("Total"),
            'invoice_label': _("INVOICE"),
            'invoice_date_label': _("Date: "),
            'invoice_no_label': _("INVOICE No. "),
            'invoice_bill_to': _("Bill to:"),
            'invoice_ship_to': _("Ship to:"),
            'invoice_row_no_label': _("No."),
            'invoice_notes_label': _("Notes:"),
            'invoice_subtotal': _("Subtotal: "),
            'invoice_tax': _("Tax: "),
            'invoice_tax_total': _("Tax total: "),
            'invoice_total': _("Total: "),
            '$': _("SEK"),
        }
    }

    json_data = json.dumps(invoice, indent=4)
    order.invoiceData = base64.b64encode(json_data)

    order.save()

    jid = cloud.shell.execute('mvn exec:java -Dexec.args="{data}"', {'data': order.invoiceData}, return_file='report.txt', _env='maxe', cwd='/home/picloud/reporter')



#    conn = EuSQSConnection()
#    q = conn.get_queue('invoice')
#
#    if not q:
#        raise Exception('Can not get queue.')
#
#    m = Message()
#    m.set_body()
#    q.write(m)
#    conn.close()

def confirm(request):

    if not request.session.has_key('order_id'):
        return HttpResponseRedirect(reverse('orders_checkout'))

    order = Order.objects.get(pk=request.session['order_id'])
    order_url = get_order_hash_url(order)

    #    if order.status != Order.ORDER_STATUS_PAID:
    #        return HttpResponse('Wating for payment.')

    autouser = not 'autouser' in APP_SETTINGS or APP_SETTINGS['autouser'] is True

    if autouser and request.user.is_anonymous():

        user = User.objects.filter(email=order.email)
        if user.count() < 1:

            password = generate_password(6)
            user = User.objects.create_user(order.email, order.email, password)

            if not user:
                messages.add_message(request, messages.ERROR, _('Can not create a new user account.'))
                return HttpResponseRedirect(reverse('orders_checkout'))

            new_user = authenticate(username=order.email, password=password)
            user_registered_signal.send(sender=None, user=new_user,
                                        request=request)

            login(request, new_user)

            try:
                message = _(u"Hello, here is your new account for inter24.se You can use it to check your order status.\n\n  Username: %(username)s \n  Password: %(password)s \n\n\nInter24 team") % {'username': order.email, 'password': password }
                subject, from_email, to = _(u'Your new inter24.se account details'), 'info@inter24.se', order.email
                send_mail(subject, message, from_email, [to])

                messages.add_message(request, messages.INFO, _('We have created a new account for you. \n\n  Username: %(username)s\n  Password: %(password)s. You can use it to check order status.') % {'username': order.email, 'password': password })
            except SMTPRecipientsRefused:
                messages.add_message(request, messages.ERROR, _('Can not send invoice to providen email address, please check it.'))
                return HttpResponseRedirect(reverse('orders_checkout'))
        else:
            messages.add_message(request, messages.ERROR, _('User with this username already exists. PLease login first.'))
            return HttpResponseRedirect(reverse('orders_checkout'))

    shopping_cart = Cart(request)
    shopping_cart.cart.checked_out = True
    shopping_cart.cart.order = order
    shopping_cart.cart.save()

    if autouser:
        order.user = request.user.get_profile()

    order.cart = shopping_cart.cart
    order.mark_confirmed()

    if autouser:
        add_invoice_delivery_task(order)

        if order.address.temporary:
            order.address.temporary = False
        order.address.profile = request.user.get_profile()
        order.address.save()

    request.session['order_id'] = None
    request.session['prev_order_id'] = order.id

    if 'success_url' in request.session:
        return HttpResponseRedirect(request.session['success_url'])
    else:
        return HttpResponseRedirect(reverse('orders_checkout_done'))


