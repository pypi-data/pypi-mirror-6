from django.db import models
from django.utils.six import with_metaclass
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError

from .subclassing import SubfieldBase
from .settings import kv_settings

serialize = kv_settings['SERIALIZE_FUNCTION']
deserialize = kv_settings['DESERIALIZE_FUNCTION']


class SerializableField(with_metaclass(SubfieldBase, models.TextField)):
    """
    A model field that restores it's type upon loading from the database.

    This field extends TextField so it's saved in the database as a text field.
    """

    def pre_init(self, value, obj):
        """
        deserializes the value saved after loading from the database,
        this function uses the DESERIALIZE_FUNCTION in the settings if one is
        provided.
        ValidationError is thrown if the value could not be deserialized.
        """
        if obj._state.adding:
            # Make sure the primary key actually exists on the object before
            # checking if it's empty. This is a special case for South
            # datamigrations
            # this is also inspired by
            # https://github.com/bradjasper/django-jsonfield/
            if not hasattr(obj, "pk") or obj.pk is not None:
                try:
                    return deserialize(value)
                except ValueError:
                    raise ValidationError(_("could not deserialize the given \
                    value."))

        return value

    def to_python(self, value):
        return value

    def get_prep_value(self, value):
        return self.value_to_string(value)

    def value_to_string(self, obj):
        """
        serializes object before saving, this function uses the
        SERIALIZE_FUNCTION in settings if one is provided.
        ValidationError is thrown if the value could not be serialized.
        """
        try:
            return serialize(obj)
        except ValueError:
            raise ValidationError(_("could not serialize the given value."))

    def __unicode__(self):
        return self.value_to_string(self.value)
