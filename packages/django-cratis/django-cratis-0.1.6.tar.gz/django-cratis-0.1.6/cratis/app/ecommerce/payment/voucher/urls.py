from django.conf.urls.defaults import patterns, url
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from cratis.app.ecommerce.payment.voucher.views import VoucherStart


urlpatterns = patterns('cratis.app.ecommerce.payment.voucher.views',
    url(r'^(?P<method>[^\\]+)/pay', never_cache(VoucherStart.as_view()), name='voucher_payment_start')
)



