from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('',
    (r'^ipn/notify/8372983hfjewhfew83/', include('paypal.standard.ipn.urls')),
)

urlpatterns += patterns('cratis.app.ecommerce.payment.paypal.views',
    url(r'^(?P<method>[^\\]+)/start', 'payment_start', name='paypal_payment_start'),
    url(r'^(?P<method>[^\\]+)/confirm', 'payment_confirm', name='paypal_payment_confirm'),
)


