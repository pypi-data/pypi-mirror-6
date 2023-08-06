import re

from django.db.models import CharField
from django.forms.fields import RegexField

from widgets import ColorFieldWidget

RGB_REGEX = re.compile('^#?((?:[0-F]{3}){1,2})$', re.IGNORECASE)


class RGBColorField(CharField):

    #widget = ColorFieldWidget

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 7
        self.default_value = kwargs.pop("default_value", None)
        super(RGBColorField, self).__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        kwargs.update({
                      'form_class': RegexField,
                      'widget': ColorFieldWidget({'value': self.default_value}),
                      'regex': RGB_REGEX,
                      })
        return super(RGBColorField, self).formfield(**kwargs)

try:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules([], ["^colorful\.fields\.RGBColorField"])
except ImportError:
    pass
