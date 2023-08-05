# -*- coding: utf-8 -*-

import json

from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.forms.fields import Field
from django.forms.util import ValidationError as FormValidationError
from django.utils.translation import ugettext as _


class JSONFormField(Field):
    def clean(self, value):

        if not value and not self.required:
            return None

        value = super(JSONFormField, self).clean(value)

        if isinstance(value, basestring):
            try:
                json.loads(value)
            except ValueError:
                raise FormValidationError(_("Enter valid JSON"))
        return value


class JSONField(models.TextField):
    """JSONField is a generic textfield that serializes/unserializes JSON objects"""

    # Used so to_python() is called
    __metaclass__ = models.SubfieldBase

    def __init__(self, *args, **kwargs):
        self.dump_kwargs = kwargs.pop('dump_kwargs', {'cls': DjangoJSONEncoder})
        self.load_kwargs = kwargs.pop('load_kwargs', {})

        super(JSONField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        """Convert string value to JSON"""
        if isinstance(value, basestring):
            try:
                return json.loads(value, **self.load_kwargs)
            except ValueError:
                pass
        return value

    def get_db_prep_value(self, value, connection, prepared=False):
        """Convert JSON object to a string"""

        if isinstance(value, basestring):
            return value
        return json.dumps(value, **self.dump_kwargs)

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return self.get_prep_value(value)

    def value_from_object(self, obj):
        return json.dumps(super(JSONField, self).value_from_object(obj))

    def formfield(self, **kwargs):

        if "form_class" not in kwargs:
            kwargs["form_class"] = JSONFormField

        field = super(JSONField, self).formfield(**kwargs)

        if not field.help_text:
            field.help_text = "Enter valid JSON"

        return field

try:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules([], ["^jsonfield\.fields\.JSONField"])
except ImportError:
    pass
