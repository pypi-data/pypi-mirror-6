from django.contrib import admin
from django.forms import TextInput, Textarea
from suit.admin import SortableModelAdmin
from .fields import default_overrides, fix_translations
from cratis.app.i18n.translate import TranslatableAdmin, InlineTranslations
from cratis.app.ecommerce.payment.models import PaymentLog, PaymentMethod, PaymentMethodTranslation, PaymentMethodKey
from django.db import models

class PaymentLogAdmin(admin.ModelAdmin):
    ordering = ('-id',)
    list_display = ('module', 'operation', 'url', 'user_ip', 'user_id', 'date_created')

admin.site.register(PaymentLog, PaymentLogAdmin)


class InlinePaymentMethodTranslation(InlineTranslations):
    model = PaymentMethodTranslation
    suit_classes = 'suit-tab suit-tab-translations'
    formfield_overrides = default_overrides


class InlinePaymentMethodKey(admin.StackedInline):
    model = PaymentMethodKey
    suit_classes = 'suit-tab suit-tab-keys'
    formfield_overrides = {
            models.CharField: {'widget': TextInput(attrs={'class': 'span5'})},
            models.TextField: {'widget': Textarea(attrs={'class': 'span7'})},
    }
    extra = 1


class PaymentMethodAdmin(SortableModelAdmin, TranslatableAdmin):
    formfield_overrides = default_overrides
    inlines = [InlinePaymentMethodTranslation, InlinePaymentMethodKey]
    init_translations = ['name', 'description']
    translation_class = PaymentMethodTranslation
    list_display = ('name', 'method', 'enabled')
    actions = [fix_translations]

    sortable = 'sorting'

    fieldsets = (
        (None, {
            'classes': ('suit-tab suit-tab-general',),
            'fields': (
                'name', 'slug', 'method', 'enabled', 'logo', 'picture', 'description')
        }),
        ('Configuration', {
            'classes': ('suit-tab suit-tab-config',),
            'fields': ('config', )
        })
    )

    suit_form_tabs = (
        ('general', 'General'),
        ('config', 'Configuration'),
        ('keys', 'Keys'),
        ('translations', 'Translations')
    )

    def response_post_save_add(self, request, obj):
        return super(PaymentMethodAdmin, self).response_post_save_add(request, obj)


admin.site.register(PaymentMethod, PaymentMethodAdmin)