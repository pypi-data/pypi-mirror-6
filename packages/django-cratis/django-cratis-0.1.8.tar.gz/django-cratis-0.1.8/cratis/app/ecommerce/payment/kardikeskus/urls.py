from django.conf.urls.defaults import patterns, url
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from cratis.app.ecommerce.payment.kardikeskus.views import KardikeskusStart, KardikeskusCallback


urlpatterns = patterns('cratis.app.ecommerce.payment.kardikeskus.views',
    url(r'^(?P<method>[^\\]+)/start', never_cache(KardikeskusStart.as_view()), name='kardikeskus_payment_start'),
    url(r'^(?P<method>[^\\]+)/callback', csrf_exempt(never_cache(KardikeskusCallback.as_view())), name='kardikeskus_payment_callback'),
)



