from cms.models.fields import PageField
from django.db import models
from django.db.models.fields import DateTimeField

from django.utils.translation import ugettext_lazy as _
from filer.fields.image import FilerImageField
from cratis.app.i18n.translate import TranslatableModelMixin


class Banner(TranslatableModelMixin, models.Model):
    date_created = DateTimeField(auto_now_add=True)
    date_updated = DateTimeField(auto_now=True)

    name = models.CharField(max_length=255)

    def __unicode__(self):
        return self.name + ', id: ' + str(self.id)

    class Meta:
        verbose_name = _('Banner')
        verbose_name_plural = _('Banners')


class BannerImage(models.Model):
    #    title = models.CharField(max_length=100, blank=True)
    image = FilerImageField(null=True, blank=True)
    banner = models.ForeignKey(Banner)
    title = models.CharField(max_length=100, blank=True, default='', null=False)
    page = PageField(blank=True, null=True)
    url = models.CharField(max_length=100, blank=True, null=True)

    def get_url(self):
        if self.url:
            return self.url
        else:
            return '#'

    class Meta:
        verbose_name = _('Slide')
        verbose_name_plural = _('Slides')
