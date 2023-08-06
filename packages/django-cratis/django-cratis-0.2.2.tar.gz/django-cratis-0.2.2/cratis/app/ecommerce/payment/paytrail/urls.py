from django.conf.urls.defaults import patterns, url
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from cratis.app.ecommerce.payment.paytrail.views import PaytrailStart, PaytrailCallback, PaytrailAccept, PaytrailCancel


urlpatterns = patterns('cratis.app.ecommerce.payment.paytrail.views',
    url(r'^(?P<method>[^\\]+)/start', never_cache(PaytrailStart.as_view()), name='paytrail_payment_start'),
    url(r'^(?P<method>[^\\]+)/accept', csrf_exempt(never_cache(PaytrailAccept.as_view())), name='paytrail_payment_accept'),
    url(r'^(?P<method>[^\\]+)/cancel', csrf_exempt(never_cache(PaytrailCancel.as_view())), name='paytrail_payment_cancel'),
    url(r'^(?P<method>[^\\]+)/callback', csrf_exempt(never_cache(PaytrailCallback.as_view())), name='paytrail_payment_callback'),
)



