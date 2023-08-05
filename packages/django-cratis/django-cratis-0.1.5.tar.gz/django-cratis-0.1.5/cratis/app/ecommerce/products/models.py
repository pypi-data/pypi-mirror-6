from django.core.urlresolvers import reverse
from django.core.validators import RegexValidator
from django.db import models
from django.db.models.fields import DateTimeField
from django.utils.safestring import mark_safe

from django.utils.translation import ugettext_lazy as _
from filer.fields.image import FilerImageField
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel
from cratis.app.i18n.translate import TranslatableModelMixin, _languages
from cratis.app.i18n.templatetags.model_trans import localize


class ProductAttributeTypeTranslation(models.Model):
    lang = models.CharField(max_length=2, editable=False)
    related = models.ForeignKey('ProductAttributeType', null=True, related_name='translations')
    name = models.CharField(max_length=255, verbose_name=_('name'))


class ProductAttributeType(models.Model):
    name = models.CharField(max_length=100, verbose_name=_('name'))
    values = models.ManyToManyField('ProductAttributeValue')

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _('Product attribute')
        verbose_name_plural = _('Product attributes')

    @staticmethod
    def get_translation_class():
        return ProductAttributeTypeTranslation


class ProductAttributeValue(models.Model):
    type = models.ForeignKey(ProductAttributeType, null=True)
    value = models.CharField(max_length=100, verbose_name=_('value'))

    def __unicode__(self):
        return self.value


class ProductAttributeFilter(models.Model):
    name = models.CharField(max_length=100, verbose_name=_('name'))

    attributes = models.ManyToManyField('ProductAttributeType', null=True, blank=True, verbose_name=_('Attributes'))
    categories = models.ManyToManyField('ProductCategory', blank=True, null=True, verbose_name=_('Show for categories'),
                                        related_name='filters')

    order_index = models.IntegerField(verbose_name=_('Ordering index'), default=0)

    class Meta:
        ordering = ('order_index', 'name')

    def __unicode__(self):
        return self.name


class ProductAttribute(models.Model):
    product = models.ForeignKey('Product', null=True, related_name='attributes')
    type = models.ForeignKey(ProductAttributeType, null=True)
    value = models.CharField(max_length=255, verbose_name=_('value'), null=True, blank=True)

    # class Meta:
    #     ordering = ('value', )

    def __unicode__(self):
        return self.type.name


slug_validator = RegexValidator(regex='^[^\d/][^/]+$',
                                message=_('Slug should not start with digit and contain "/" character'))


class ProductCategoryTranslation(models.Model):
    lang = models.CharField(max_length=2, editable=False)
    related = models.ForeignKey('ProductCategory', null=True, related_name='translations')
    name = models.CharField(max_length=255, verbose_name=_('name'))
    description = models.TextField(blank=True, default='')
    slug = models.CharField(max_length=255, verbose_name=_('slug'), default='', blank=True, validators=[slug_validator])


class ProductCategory(TranslatableModelMixin, MPTTModel):
    date_created = DateTimeField(auto_now_add=True)
    date_updated = DateTimeField(auto_now=True)

    order_index = models.IntegerField(verbose_name=_('Ordering index'), default=0)

    name = models.CharField(max_length=255, verbose_name=_('name'))
    description = models.TextField(blank=True, default='')
    slug = models.CharField(max_length=255, verbose_name=_('slug'), default='', blank=True, validators=[slug_validator])

    image = FilerImageField(null=True, blank=True)

    parent = TreeForeignKey('self', null=True, blank=True, related_name='children')

    is_active = models.BooleanField(default=False, verbose_name=_('Is active'))

    attribute_types = models.ManyToManyField(ProductAttributeType, verbose_name=_('Product attributes'), null=True,
                                             blank=True, related_name='categories', symmetrical=False)

    allow_filtering = models.BooleanField(default=True, verbose_name=_('Allow filter by'))

    # It is required to rebuild tree after save, when using order for mptt-tree
    def save(self, *args, **kwargs):
        super(ProductCategory, self).save(*args, **kwargs)
        ProductCategory.objects.rebuild()


    def get_absolute_url(self):
        category_slug = localize(self, 'slug')
        if category_slug != '':
            return reverse('products_in_category_by_slug', kwargs={'category_slug': category_slug})
        else:
            return reverse('products_in_category', kwargs={'category_id': self.pk})

    def recursive_category_list(self):
        if self.parent:
            all = [self]
            for cat in self.parent.recursive_category_list():
                all.append(cat)
            return all
        else:
            return [self]

        #    parents_list.short_description = 'Parent categories'

    def get_own_and_parents_filters(self):
        attributes = list(self.filters.all())
        if self.parent:
            attributes += list(self.parent.get_own_and_parents_filters())
        return attributes

    @staticmethod
    def get_translation_class():
        return ProductCategoryTranslation

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _('Product category')
        verbose_name_plural = _('Product categories')
        ordering = ['order_index']

    class MPTTMeta:
        order_insertion_by = ['order_index']


class ProductTranslation(models.Model):
    lang = models.CharField(max_length=2, editable=False)
    related = models.ForeignKey('Product', null=True, related_name='translations')
    title = models.CharField(max_length=255, blank=True, null=True)
    long_title = models.CharField(max_length=255, blank=True, null=True, default='')
    slug = models.CharField(max_length=255, verbose_name=_('slug'), null=True, blank=True, validators=[slug_validator])
    description = models.TextField(blank=True, null=True)
    long_description = models.TextField(blank=True, null=True)

    def __unicode__(self):

        return _languages[self.lang]

    # def title(self):
    #     return smart_str(self.title)
    #
    # def long_title(self):
    #     return smart_str(self.long_title)
    #
    # def description(self):
    #     return smart_str(self.description)
    #
    # def long_description(self):
    #     return smart_str(self.long_description)

class Product(TranslatableModelMixin, models.Model):
    date_created = DateTimeField(auto_now_add=True)
    date_updated = DateTimeField(auto_now=True)

    title = models.CharField(max_length=255)
    long_title = models.CharField(max_length=255)
    slug = models.CharField(max_length=255, verbose_name=_('slug'), default='', blank=True, validators=[slug_validator])
    description = models.TextField(blank=True)
    long_description = models.TextField(blank=True)

    price = models.DecimalField(max_digits=8, decimal_places=2)
    price_discount = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    discount = models.IntegerField(default=0)

    categories = models.ManyToManyField(ProductCategory, blank=True, null=True)

    related = models.ManyToManyField('Product', blank=True, null=True)

    featured = models.BooleanField(default=False, verbose_name=_('Featured'))
    sold = models.BooleanField(default=False, verbose_name=_('Is sold'))
    active = models.BooleanField(default=False, verbose_name=_('Is active'))
    archived = models.BooleanField(default=False, verbose_name=_('Is archived'))
    sold_count = models.PositiveIntegerField(verbose_name=_('Sold count'), default=0)

    #    def title(self):
    #        return smart_str(self.title)
    #
    #    def long_title(self):
    #        return smart_str(self.long_title)
    #
    #    def description(self):
    #        return smart_str(self.description)
    #
    #    def long_description(self):
    #        return smart_str(self.long_description)

    def get_absolute_url(self):
        product_slug = localize(self, 'slug')

        if self.categories.count() < 1:
            return '/product/' + str(self.pk)

        category = self.categories.all()[0]
        category_slug = localize(category, 'slug')

        if category_slug != '' and product_slug != '':
            return reverse('product_with_cat_both_by_slug',
                           kwargs={'slug': product_slug, 'category_slug': category_slug})

        elif category_slug != '':
            return reverse('product_with_cat_cat_by_slug_prod_by_id',
                           kwargs={'pk': self.pk, 'category_slug': category_slug})

        elif product_slug != '':
            return reverse('product_with_cat_cat_by_id_prod_by_slug',
                           kwargs={'slug': product_slug, 'category_id': category.pk})

        else:
            return reverse('product_with_cat',
                           kwargs={'pk': self.pk, 'category_id': category.pk})

    def has_discount(self):
        return self.discount > 0 or self.price_discount > 0

    def discount_price(self):
        if self.price_discount > 0:
            return self.price_discount
        return self.price - self.price * self.discount / 100

    def slug_list(self):
        return ', '.join([self.slug] + [trans.slug + ' (' + trans.lang + ')' for trans in self.translations.all() if
                                        trans.slug and trans.slug != ''])

    def category_list(self):
        return ', '.join([cat.name for cat in self.categories.all()])

    category_list.short_description = 'Categories'

    @staticmethod
    def get_translation_class():
        return ProductTranslation

    def __unicode__(self):
        return self.title + ', id: ' + str(self.id)

    class Meta:
        verbose_name = _('Product')
        verbose_name_plural = _('Products')


class ProductImage(models.Model):
#    title = models.CharField(max_length=100, blank=True)
    image = FilerImageField(null=True, blank=True)
    sorting = models.PositiveIntegerField(verbose_name=_('Sorting'), default=0)
    product = models.ForeignKey(Product)

    class Meta:
        ordering = ('-sorting', )


