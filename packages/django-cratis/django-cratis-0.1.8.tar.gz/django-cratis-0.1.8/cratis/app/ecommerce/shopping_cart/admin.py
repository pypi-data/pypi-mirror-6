from models import Item
from models import Cart
from cratis.app.core.common.i18n import message_wrapper
from django.contrib import admin


#class ProductCategoryAdmin(AdminImageMixin, admin.ModelAdmin):
#    pass
#

class InlineProduct(admin.TabularInline):
    model = Item
    extra = 0

class CartAdmin(admin.ModelAdmin):
    inlines = [InlineProduct]

    def queryset(self, request):
        qs = super(CartAdmin, self).queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(author=request.user)

    def has_add_permission(self, request):
        return False




#    class Media:
#        js = ("js/admin/product_form.js",)

admin.site.register(Cart, CartAdmin)

#admin.site.register(Product, ProductAdmin)
#admin.site.register(ProductCategory, ProductCategoryAdmin)

#admin.site.register = I18nLabel(admin.site.register).register()
#admin.site.app_index = I18nLabel(admin.site.app_index).index()
admin.ModelAdmin.message_user = message_wrapper(admin.ModelAdmin.message_user)