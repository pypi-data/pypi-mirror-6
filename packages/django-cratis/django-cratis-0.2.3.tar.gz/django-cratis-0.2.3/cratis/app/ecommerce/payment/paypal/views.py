from urllib import urlencode
from django.core.urlresolvers import reverse
from django import forms
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from paypal.pro.exceptions import PayPalFailure
from paypal.pro.fields import CountryField, CreditCardField, CreditCardExpiryField, CreditCardCVV2Field
from paypal.pro.forms import ConfirmForm
from paypal.pro.helpers import SANDBOX_ENDPOINT, ENDPOINT, PayPalWPP, VERSION
from cratis import settings
from cratis.app.ecommerce.payment.models import PaymentMethod
from paypal.pro.views import PayPalPro, SANDBOX_EXPRESS_ENDPOINT, EXPRESS_ENDPOINT
from cratis.app.ecommerce.orders.models import Order


class PayPalView(PayPalWPP):

    def __init__(self, request, params):
        """Required - USER / PWD / SIGNATURE / VERSION"""
        self.request = request
        if params['TEST']:
            self.endpoint = SANDBOX_ENDPOINT
        else:
            self.endpoint = ENDPOINT

        self.signature_values = {
            'USER': params['USER'],
            'PWD': params['PASSWORD'],
            'SIGNATURE': params['SIGNATURE'],
            'VERSION': params['VERSION'],
        }
        self.signature = urlencode(self.signature_values) + "&"


class PaymentForm(forms.Form):

    """Form used to process direct payments."""
    firstname = forms.CharField(255, label="First Name")
    lastname = forms.CharField(255, label="Last Name")
    street = forms.CharField(255, label="Street Address")
    city = forms.CharField(255, label="City")
    state = forms.CharField(255, label="State")
    countrycode = CountryField(label="Country", initial="US")
    zip = forms.CharField(32, label="Postal / Zip Code")
    acct = CreditCardField(label="Credit Card Number")
    expdate = CreditCardExpiryField(label="Expiration Date")
    cvv2 = CreditCardCVV2Field(label="Card Security Code")

    def process(self, request, item):
        """Process a PayPal direct payment."""
        wpp = PayPalView(request, params=PaymentForm.cc_config)
        params = self.cleaned_data
        params['creditcardtype'] = self.fields['acct'].card_type
        params['expdate'] = self.cleaned_data['expdate'].strftime("%m%Y")
        params['ipaddress'] = request.META.get("REMOTE_ADDR", "")
        params.update(item)

        try:
            # Create single payment:
            if 'billingperiod' not in params:
                nvp_obj = wpp.doDirectPayment(params)
            # Create recurring payment:
            else:
                nvp_obj = wpp.createRecurringPaymentsProfile(
                    params, direct=True)
        except PayPalFailure:
            return False
        return True


class PayPalProView(PayPalPro):

    def __init__(
        self, config=None, item=None, payment_form_cls=PaymentForm, payment_template="pro/payment.html",
        confirm_form_cls=ConfirmForm, confirm_template="pro/confirm.html", success_url="?success",
        fail_url=None, context=None, form_context_name="form"):

        config['VERSION'] = VERSION
        self.cc_config = config

        PaymentForm.cc_config = config

        super(
            PayPalProView, self).__init__(item, payment_form_cls, payment_template, confirm_form_cls,
                                          confirm_template, success_url, fail_url, context, form_context_name)

    def get_endpoint(self):
        if self.cc_config['TEST']:
            return SANDBOX_EXPRESS_ENDPOINT
        else:
            return EXPRESS_ENDPOINT

    def redirect_to_express(self):
        """
        First step of ExpressCheckout. Redirect the request to PayPal using the
        data returned from setExpressCheckout.
        """
        wpp = PayPalView(self.request, params=self.cc_config)

        try:
            nvp_obj = wpp.setExpressCheckout(self.item)
        except PayPalFailure as e:
            self.context['errors'] = self.errors['paypal']
            return self.render_payment_form()
        else:
            pp_params = dict(token=nvp_obj.token, AMT=self.item['amt'],
                             RETURNURL=self.item['returnurl'],
                             CANCELURL=self.item['cancelurl'])
            pp_url = self.get_endpoint() % urlencode(pp_params)
            return HttpResponseRedirect(pp_url)

    def render_confirm_form(self):
        """
        Second step of ExpressCheckout. Display an order confirmation form which
        contains hidden fields with the token / PayerID from PayPal.
        """
        initial = dict(token=self.request.GET[
                       'token'], PayerID=self.request.GET['PayerID'])
        self.context[self.form_context_name] = self.confirm_form_cls(
            initial=initial)
        return render_to_response(self.confirm_template, self.context, RequestContext(self.request))

    def validate_confirm_form(self):
        """
        Third and final step of ExpressCheckout. Request has pressed the confirmation but
        and we can send the final confirmation to PayPal using the data from the POST'ed form.
        """
        wpp = PayPalView(self.request, params=self.cc_config)
        pp_data = dict(token=self.request.POST[
                       'token'], payerid=self.request.POST['PayerID'])
        self.item.update(pp_data)

        # @@@ This check and call could be moved into PayPalWPP.
        try:
            if self.is_recurring():
                nvp_obj = wpp.createRecurringPaymentsProfile(self.item)
            else:
                nvp_obj = wpp.doExpressCheckoutPayment(self.item)
        except PayPalFailure:
            self.context['errors'] = self.errors['processing']
            return self.render_payment_form()
        else:
            return HttpResponseRedirect(self.success_url)


def paypal_view_data(request, method):

    payment = get_object_or_404(PaymentMethod, slug=method)
    config = payment.behavior().config

    order = Order.objects.get(pk=request.session['order_id'])

    detalisation = order.get_detalisation()
    host = request.META['HTTP_HOST']

    item = {"amt": detalisation['full_total'],  # amount to charge for item
            "inv": order.id,  # unique tracking variable paypal
            "cart": order.cart,
            "currencycode": settings.APP_SETTINGS['currency'].upper(),
            # "custom": "tracking",       # custom tracking variable for you
            # Express checkout cancel url
            "cancelurl": "http://%s%s" % (host, reverse('orders_checkout')),
            "returnurl": "http://%s/payment/paypal/confirm" % host}  # Express checkout return url

    i = 0
    for row in order.cart.items.all():
        item['L_NAME' + str(i)] = row.product.title
        item['L_AMT' + str(i)] = str(row.unit_price)
        item['L_QTY' + str(i)] = row.quantity
        if row.delivery_method:
            i += 1
            item['L_NAME' + str(i)] = 'Delivery of ' + \
                row.product.title + \
                ' with %s' % row.delivery_method.name
            item['L_AMT' + str(i)] = str(row.delivery_method.delivery_price)
            item['L_QTY' + str(i)] = row.quantity
        i += 1

    # return PayPalPro(item=item,
    # success_url=reverse('cratis.app.ecommerce.orders.views.confirm'))
    return PayPalProView(item=item, success_url=reverse('cratis.app.ecommerce.orders.views.confirm'), config=config)


@never_cache
def payment_start(request, method):
    ppp = paypal_view_data(request, method)
    return ppp(request)


@csrf_exempt
@never_cache
def payment_confirm(request, method):
    ppp = paypal_view_data(request, method)
    return ppp(request)
