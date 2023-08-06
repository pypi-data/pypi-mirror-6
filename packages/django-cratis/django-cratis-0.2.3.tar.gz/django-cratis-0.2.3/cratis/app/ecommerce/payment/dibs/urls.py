from django.conf.urls.defaults import patterns, url
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from cratis.app.ecommerce.payment.dibs.views import DibsStart, DibsAccept, DibsCancel, DibsCallback

urlpatterns = patterns('cratis.app.ecommerce.payment.dibs.views',
    url(r'^(?P<method>[^\\]+)/start', never_cache(DibsStart.as_view()), name='dibs_payment_start'),
    url(r'^(?P<method>[^\\]+)/accept', csrf_exempt(never_cache(DibsAccept.as_view())), name='dibs_payment_accept'),
    url(r'^(?P<method>[^\\]+)/cancel', csrf_exempt(never_cache(DibsCancel.as_view())), name='dibs_payment_cancel'),
    url(r'^(?P<method>[^\\]+)/callback', csrf_exempt(never_cache(DibsCallback.as_view())), name='dibs_payment_callback'),
)


