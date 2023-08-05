
from django.conf.urls import url, patterns, include
from cratis.app.i18n.utils import localize_url as _


urlpatterns = patterns('',

    url(_(r'^profile/$'), 'allauth.account.views.email', name='profile')
)
