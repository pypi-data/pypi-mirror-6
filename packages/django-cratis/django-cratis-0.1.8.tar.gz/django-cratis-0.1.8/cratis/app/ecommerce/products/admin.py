from django.forms import TextInput
from mptt.admin import MPTTModelAdmin
from suit.admin import SortableTabularInline, SortableModelAdmin
from cratis.app.utils.admin import default_overrides, fix_translations
from cratis.app.i18n.translate import TranslatableAdmin, InlineTranslations
from cratis.app.i18n.utils import I18nLabel, message_wrapper
from django.contrib import admin
from models import Product, ProductCategory, ProductImage, ProductTranslation, ProductAttributeFilter
from cratis.app.ecommerce.products.models import ProductCategoryTranslation, ProductAttribute, ProductAttributeType, ProductAttributeValue, ProductAttributeTypeTranslation


class InlineProductCategoryTranslation(InlineTranslations):
    model = ProductCategoryTranslation


class ProductCategoryAdmin(TranslatableAdmin, MPTTModelAdmin, SortableModelAdmin):

    formfield_overrides = default_overrides
    inlines = [InlineProductCategoryTranslation]
    init_translations = ['name', 'description']
    translation_class = ProductCategoryTranslation
    fields = ('name', 'description', 'slug', 'image', 'parent', 'attribute_types', 'allow_filtering')

    list_display = ('name', 'translation_list', 'is_active')
    list_editable = ('is_active',)
    actions = [fix_translations]

    search_fields = ('name', 'slug', '=id')

    sortable = 'order_index'
    mptt_level_indent = 20


class InlineProductImage(SortableTabularInline):
    model = ProductImage
    extra = 2
    classes = ['collapse']

    suit_classes = 'suit-tab suit-tab-images'

    sortable = 'sorting'




class InlineProductTranslation(InlineTranslations):
    model = ProductTranslation
    suit_classes = 'suit-tab suit-tab-translations'
    formfield_overrides = default_overrides


class InlineProductAttributeTypeTranslation(InlineTranslations):
    model = ProductAttributeTypeTranslation


def set_featured(modeladmin, request, queryset):
    queryset.update(featured=True)


set_featured.short_description = "Set featured"


def make_active(modeladmin, request, queryset):
    queryset.update(active=True)


make_active.short_description = "Set active"


def make_inactive(modeladmin, request, queryset):
    queryset.update(active=False)


make_inactive.short_description = "Set inactive"


def reset_featured(modeladmin, request, queryset):
    queryset.update(featured=False)


reset_featured.short_description = "Clear featured"


def set_not_sold(modeladmin, request, queryset):
    queryset.update(sold=False)


set_not_sold.short_description = "Set not sold"


def set_sold(modeladmin, request, queryset):
    queryset.update(sold=True)
set_sold.short_description = "Set sold"


def set_archived(modeladmin, request, queryset):
    queryset.update(archived=True, active=False, slug='')
set_archived.short_description = "Remove (archive) products"


class InlineAttribute(admin.TabularInline):

    formfield_overrides = default_overrides
    model = ProductAttribute
    extra = 1

    suit_classes = 'suit-tab suit-tab-attr'

    def formfield_for_manytomany(self, db_field, request=None, **kwargs):
        if db_field.name == "values":
            kwargs["queryset"] = ProductAttributeValue.objects.filter(type=self.model._get_pk_val())
        return super(InlineAttribute, self).formfield_for_manytomany(db_field, request, **kwargs)


class ProductAttributeTypeAdmin(TranslatableAdmin, admin.ModelAdmin):

    formfield_overrides = default_overrides
    inlines = [InlineProductAttributeTypeTranslation]
    ordering = ['name']

    fields = ('name',)
    init_translations = ['name']
    translation_class = ProductAttributeTypeTranslation
    actions = [fix_translations, ]

    search_fields = ('name', )


class ProductAdmin(TranslatableAdmin, admin.ModelAdmin):
    inlines = [InlineAttribute, InlineProductTranslation, InlineProductImage]
    init_translations = ['title', 'long_title', 'description', 'long_description']
    translation_class = ProductTranslation
    formfield_overrides = default_overrides

    def queryset(self, request):
        return super(ProductAdmin, self).queryset(request).filter(archived=False)


    list_filter = ('active', 'categories', 'sold', 'featured')
    list_display = ('title', 'long_title', 'id', 'slug_list', 'price', 'category_list', 'active', 'sold', 'featured')

    search_fields = ('title', '=id', 'categories__name')

    actions = [fix_translations, set_featured, reset_featured, set_sold, set_not_sold, make_active, make_inactive, set_archived]

    fieldsets = (
        (None, {
            'classes': ('suit-tab suit-tab-general',),
            'fields': (
                'title', 'long_title', 'slug', 'description', 'long_description', 'categories')
        }),
        ('Avalibility', {
            'classes': ('suit-tab suit-tab-general',),
            'fields': (
                'sold', 'active')
        }),
        ('Pricing', {
            'classes': ('suit-tab suit-tab-pricing',),
            'fields': ('price', 'price_discount', 'discount')
        }),
        ('Promotion', {
            'classes': ('suit-tab suit-tab-pricing',),
            'fields': ('related', 'featured', 'sold_count', )
        })
    )

    suit_form_tabs = (
        ('general', 'General'),
        ('pricing', 'Pricing & Promotion'),
        ('attr', 'Attributes'),
        ('translations', 'Translations'),
        ('images', 'Pictures'),
    )

    # suit_form_includes = (
    #     ('admin/trans_info.html', 'top', 'translations'),
    # )

    # class Media:
    #     js = (
            # "js/admin/product_form.js",
            # "js/admin/tiny_mce/tiny_mce.js",
            # "js/admin/tinymce_init.js",
            # '/media/admin/custom/js/inlinecollapsed.js',
        # )


admin.site.register(Product, ProductAdmin)
admin.site.register(ProductAttributeType, ProductAttributeTypeAdmin)
admin.site.register(ProductAttributeFilter)
admin.site.register(ProductCategory, ProductCategoryAdmin)

# admin.site.register = I18nLabel(admin.site.register).register()
# admin.site.app_index = I18nLabel(admin.site.app_index).index()
admin.ModelAdmin.message_user = message_wrapper(admin.ModelAdmin.message_user)