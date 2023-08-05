from django.test import TestCase
from django.db import models

from .serializers import json_serialize, json_deserialize
from .models import KVModel
from .fields import SerializableField

class KVModelConcrete(KVModel):
    """
    a class that extends KVModel and is used
    for testing purposses only
    """

class ModelWithSerializableField(models.Model):
    """
    this class is used to test the serialzible field
    """

    value = SerializableField()

class TestSerializer(TestCase):

    def test_serialize_desialize_int(self):
        value = 12
        serialized = '12'
        self.assertEquals(json_serialize(value), serialized)
        self.assertEquals(json_deserialize(serialized), value)

    def test_serialize_desialize_boolean(self):
        value = True
        serialized = 'true'
        self.assertEquals(json_serialize(value), serialized)
        self.assertEquals(json_deserialize(serialized), value)

    def test_serialize_desialize_string(self):
        value = 'True'
        serialized = '"True"'
        self.assertEquals(json_serialize(value), serialized)
        self.assertEquals(json_deserialize(serialized), value)

    def test_serialize_desialize_float(self):
        value = 12.32
        serialized = '12.32'
        self.assertEquals(json_serialize(value), serialized)
        self.assertEquals(json_deserialize(serialized), value)

    def test_serialize_desialize_empty_string(self):
        value = ''
        serialized = '""'
        self.assertEquals(json_serialize(value), serialized)
        self.assertEquals(json_deserialize(serialized), value)

    def test_serialize_desialize_empty_zero(self):
        value = 0
        serialized = '0'
        self.assertEquals(json_serialize(value), serialized)
        self.assertEquals(json_deserialize(serialized), value)

    def test_serialize_desialize_array(self):
        value = [1, 3, 'man', True]
        serialized = '[1, 3, "man", true]'
        self.assertEquals(json_serialize(value), serialized)
        self.assertEquals(json_deserialize(serialized), value)

    def test_serialize_desialize_empty_array(self):
        value = []
        serialized = '[]'
        self.assertEquals(json_serialize(value), serialized)
        self.assertEquals(json_deserialize(serialized), value)

    def test_serialize_None(self):
        value = None
        serialized = 'null'
        self.assertEquals(json_serialize(value), serialized)
        self.assertEquals(json_deserialize(serialized), value)

    def test_serialize_empty_dict(self):
        value = {}
        serialized = '{}'
        self.assertEquals(json_serialize(value), serialized)
        self.assertEquals(json_deserialize(serialized), value)

    def test_serialize_dict(self):
        value = {'a': 123, 'b': '234'}
        self.assertEquals(json_deserialize(json_serialize(value)), value)

class TestSerializableField(TestCase):

    def test_int(self):
        value = 100000
        obj = ModelWithSerializableField(value=value)
        obj.save()
        self.assertEquals(value, obj.value)

        obj = ModelWithSerializableField.objects.first()
        self.assertEquals(value, obj.value)

    def test_string(self):
        value = '"";string"'
        obj = ModelWithSerializableField(value=value)
        obj.save()
        self.assertEquals(value, obj.value)

        obj = ModelWithSerializableField.objects.first()
        self.assertEquals(value, obj.value)

    def test_array(self):
        value = ['man', 'dragon']
        obj = ModelWithSerializableField(value=value)
        obj.save()
        self.assertEquals(value, obj.value)

        obj = ModelWithSerializableField.objects.first()
        self.assertEquals(value, obj.value)

    def test_empty_array(self):
        value = []
        obj = ModelWithSerializableField(value=value)
        obj.save()
        self.assertEquals(value, obj.value)

        obj = ModelWithSerializableField.objects.first()
        self.assertEquals(value, obj.value)

    def test_empty_string(self):
        value = ''
        obj = ModelWithSerializableField(value=value)
        obj.save()
        self.assertEquals(value, obj.value)

        obj = ModelWithSerializableField.objects.first()
        self.assertEquals(value, obj.value)

    def test_none(self):
        value = None
        obj = ModelWithSerializableField(value=value)
        obj.save()
        self.assertEquals(value, obj.value)

        obj = ModelWithSerializableField.objects.first()
        self.assertEquals(value, obj.value)

    def test_float(self):
        value = 23.43
        obj = ModelWithSerializableField(value=value)
        obj.save()
        self.assertEquals(value, obj.value)

        obj = ModelWithSerializableField.objects.first()
        self.assertEquals(value, obj.value)

    def test_zero_float(self):
        value = 0.0
        obj = ModelWithSerializableField(value=value)
        obj.save()
        self.assertEquals(value, obj.value)

        obj = ModelWithSerializableField.objects.first()
        self.assertEquals(value, obj.value)

    def test_dict(self):
        value = {'foo': 'bar', 'man': 0}
        obj = ModelWithSerializableField(value=value)
        obj.save()
        self.assertEquals(value, obj.value)

        obj = ModelWithSerializableField.objects.first()
        self.assertEquals(value, obj.value)

    def test_empyty_dict(self):
        value = {}
        obj = ModelWithSerializableField(value=value)
        obj.save()
        self.assertEquals(value, obj.value)

        obj = ModelWithSerializableField.objects.first()
        self.assertEquals(value, obj.value)

class TestKVModel(TestCase):

    def test_creating_with_a_string_value(self):
        key = 'foo'
        value = '"bar"'
        obj = KVModelConcrete(key=key, value=value)
        obj.save()
        obj = KVModelConcrete.get_by_key('foo')
        self.assertEquals(obj.value, value)

    def test_creating_with_an_int_value(self):
        key = 'foo'
        value = 1999
        obj = KVModelConcrete(key=key, value=value)
        obj.save()
        obj = KVModelConcrete.get_by_key(key=key)
        self.assertEquals(obj.value, value)

    def test_creating_with_an_int_value(self):
        key = 'foo'
        value = 1999
        obj = KVModelConcrete(key=key, value=value)
        obj.save()
        obj = KVModelConcrete.get_by_key(key=key)
        self.assertEquals(obj.value, value)

    def test_creating_with_a_float_value(self):
        key = 'foo'
        value = 1999.00
        obj = KVModelConcrete(key=key, value=value)
        obj.save()
        obj = KVModelConcrete.get_by_key(key=key)
        self.assertEquals(obj.value, value)

    def test_creating_with_a_None_value(self):
        key = 'foo'
        value = None
        obj = KVModelConcrete(key=key, value=value)
        obj.save()
        obj = KVModelConcrete.get_by_key(key=key)
        self.assertEquals(obj.value, value)
