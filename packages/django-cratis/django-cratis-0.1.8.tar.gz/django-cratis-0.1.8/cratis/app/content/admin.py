from django.contrib import admin
from cratis.app.content.models import BannerImage, Banner


class InlineBannerImage(admin.StackedInline):
    model = BannerImage
    extra = 3
    classes = ['collapse']


class BannerAdmin(admin.ModelAdmin):
    inlines = [InlineBannerImage]
    list_display = ('name',)

admin.site.register(Banner, BannerAdmin)
