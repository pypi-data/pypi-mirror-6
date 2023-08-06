
from django.conf.urls import url, patterns, include
from cratis.app.i18n.utils import localize_url as _


urlpatterns = patterns('',

    url(_(r'^profile/$'), 'cratis.app.profile.views.profile', name='profile')
)
