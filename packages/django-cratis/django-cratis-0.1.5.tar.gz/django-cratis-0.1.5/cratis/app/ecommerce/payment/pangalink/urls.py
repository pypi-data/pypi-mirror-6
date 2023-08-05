from django.conf.urls.defaults import patterns, url
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from cratis.app.ecommerce.payment.pangalink.views import PangalinkStart, PangalinkCallback


urlpatterns = patterns('cratis.app.ecommerce.payment.pangalink.views',
    url(r'^(?P<method>[^\\]+)/start', never_cache(PangalinkStart.as_view()), name='pangalink_payment_start'),
    url(r'^(?P<method>[^\\]+)/callback', csrf_exempt(never_cache(PangalinkCallback.as_view())), name='pangalink_payment_callback'),
    url(r'^(?P<method>[^\\]+)/cancel', csrf_exempt(never_cache(PangalinkCallback.as_view())), name='pangalink_payment_cancel'),
)



