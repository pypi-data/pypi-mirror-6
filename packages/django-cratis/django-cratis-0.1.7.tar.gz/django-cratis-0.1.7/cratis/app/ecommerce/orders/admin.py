from django.contrib import admin
from cratis.app.core.common.translate import TranslatableAdmin, InlineTranslations
from cratis.app.ecommerce.orders.models import Order, Address
from cratis.app.ecommerce.shopping_cart.models import  Item as CartItem, DeliveryMethod, DeliveryMethodTranslation
from cratis.app.ecommerce.orders.views import add_invoice_delivery_task

class InlineAddress(admin.StackedInline):
    model = Address
    extra = 0
#    fields = ('product', 'quantity', 'unit_price')
#    readonly_fields = ('quantity', 'unit_price', 'product',)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

class InlineOrderItems(admin.TabularInline):
    model = CartItem
    extra = 0
    fields = ('product', 'quantity', 'unit_price')
    readonly_fields = ('quantity', 'unit_price', 'product',)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


def fix_translations(modeladmin, request, queryset):
    for obj in queryset:
        modeladmin.fix_translations(obj)
fix_translations.short_description = "Fix empty translations"

def generate_invoice(modeladmin, request, queryset):
    for obj in queryset:
        add_invoice_delivery_task(obj)

generate_invoice.short_description = "Generate broken invoice"

class OrderAdmin(admin.ModelAdmin):

    list_display = ('date_created', 'email', 'full_price', 'status', 'payment_method', 'documents', 'ip_address')
    inlines = [InlineOrderItems]
    readonly_fields = ('delivery_method', 'address', 'payment_method', 'ip_address',)
    exclude = ('smartpost_box','payment_status', 'phone', 'payment_response', 'smartpost_box_name')
    list_filter = ('status', 'ip_address',)
    ordering = ('-date_created',)
    actions = [generate_invoice]



admin.site.register(Order, OrderAdmin)



class InlineDeliveryMethodTranslation(InlineTranslations):
    model = DeliveryMethodTranslation

class DeliveryMethodAdmin(TranslatableAdmin):
    inlines = [InlineDeliveryMethodTranslation]
    init_translations = ['name']
    translation_class = DeliveryMethodTranslation
    list_display = ('name', 'method', 'enabled', 'translation_list')
    actions = [fix_translations]


admin.site.register(DeliveryMethod, DeliveryMethodAdmin)



