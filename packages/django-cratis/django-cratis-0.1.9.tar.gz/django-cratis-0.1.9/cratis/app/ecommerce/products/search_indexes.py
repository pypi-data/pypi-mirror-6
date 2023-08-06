from django.utils.encoding import smart_str
from cratis.app.ecommerce.products.models import Product

__author__ = 'alex'
from haystack import indexes


class ProductIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.NgramField(document=True, use_template=True)
    categories = indexes.MultiValueField(faceted=True)
    attributes = indexes.FacetMultiValueField()
    price = indexes.IntegerField(faceted=True)
    sold = indexes.IntegerField()
    featured = indexes.BooleanField()
    discount = indexes.IntegerField(model_attr='discount')

    def get_model(self):
        return Product

    def should_update(self, instance, **kwargs):
        if not instance.active:
            self.remove_object(instance)
            return False
        return super(ProductIndex, self).should_update(instance, **kwargs)

    def index_queryset(self, **kwargs):
        return Product.objects.filter(active=True, archived=False)

    def prepare_attributes(self, obj):
        return [str(attr.type.pk) + '_' + smart_str(attr.value) for attr in obj.attributes.all()]

    def prepare_featured(self, obj):
        return True if obj.featured else False

    def prepare_sold(self, obj):
        return obj.sold_count

    def prepare_price(self, obj):
        return int(obj.price)

    def prepare_categories(self, obj):
        ids = []

        for category in obj.categories.all():
            for id in [cat.id for cat in category.recursive_category_list()]:
                ids.append(id)
        return set(ids)

