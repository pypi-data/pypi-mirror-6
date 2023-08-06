from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:

urlpatterns = patterns('',

    url(r'^payment/dibs/', include('cratis.app.ecommerce.payment.dibs.urls')),
    url(r'^payment/paypal/', include('cratis.app.ecommerce.payment.paypal.urls')),
    url(r'^payment/pangalink/', include('cratis.app.ecommerce.payment.pangalink.urls')),
    url(r'^payment/paytrail/', include('cratis.app.ecommerce.payment.paytrail.urls')),
    url(r'^payment/kk/', include('cratis.app.ecommerce.payment.kardikeskus.urls')),
    url(r'^payment/voucher/', include('cratis.app.ecommerce.payment.voucher.urls')),
)
