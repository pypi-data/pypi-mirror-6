from django_ace.widgets import AceWidget
import six
import yaml
from django.db import models
from django.core.serializers.pyyaml import DjangoSafeDumper
from django.db import models
from django.forms.widgets import TextInput
from suit_redactor.widgets import RedactorWidget
from chosen import widgets as chosenwidgets


default_overrides = {
    models.CharField: {'widget': TextInput(attrs={'class': 'span5'})},
    models.TextField: {'widget': RedactorWidget(editor_options={'lang': 'en'})},
    # models.ForeignKey: {'widget': LinkedSelect},
}

def fix_translations(modeladmin, request, queryset):
    for obj in queryset:
        modeladmin.fix_translations(obj)
fix_translations.short_description = "Fix empty translations"




class YamlFancyField(models.TextField):

    def formfield(self, **kwargs):
        kwargs["widget"] = AceWidget(mode='yaml')
        return super(YamlFancyField, self).formfield(**kwargs)

try:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules([], ["^maxe\.core\.common\.fields\.YamlFancyField"])
except ImportError:
    pass