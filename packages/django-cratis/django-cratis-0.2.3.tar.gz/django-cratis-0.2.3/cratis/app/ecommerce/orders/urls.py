from django.conf.urls.defaults import patterns, url

# Uncomment the next two lines to enable the admin:
from cratis.app.core.common.i18n import localize_url as _
from cratis.app.ecommerce.orders.views import CheckoutView, CheckoutDoneView, OrderStatusView, PaymentWaitView

urlpatterns = patterns('cratis.app.ecommerce.orders.views',

    url(r'^checkout/$',
        CheckoutView.as_view(),
        name='orders_checkout'
    ),
    url(_(r'^checkout/done$'),
        CheckoutDoneView.as_view(),
        name='orders_checkout_done'
    ),
    url(_(r'^checkout/payment/wait$'),
        PaymentWaitView.as_view(),
        name='orders_checkout_pay_wait'
    ),
    url(_(r'^checkout/status/(?P<order_id>[0-9]+)/(?P<hash>[a-f0-9]+)$'),
        OrderStatusView.as_view(),
        name='orders_status'
    ),

    url(r'^checkout/set_delivery', 'set_delivery'),
    url(_(r'^checkout/set_payment'), 'set_payment'),
    url(r'^checkout/validate', 'validate'),
#    url(r'^checkout/smartpost', 'set_smartpost_box'),
    url(r'^checkout/address', 'update_address'),
    url(r'^checkout/contacts', 'update_contacts'),
    url(_(r'^checkout/confirm'), 'confirm'),
    url(r'^checkout/payment/response', 'payment_response'),
    url(_(r'^checkout/payment/check'), 'payment_check')

)
