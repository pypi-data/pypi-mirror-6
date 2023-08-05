"""
Example
-------

class SystemSetting(KVModel):
    pass

setting = SystemSetting.create(key='foo', value=100)
loaded_setting = SystemSetting.get_by_key('foo')

"""

from django.db import models

from .fields import SerializableField


class KVModel(models.Model):
    """
    An Abstract model that has key and value fields

    key   -- Unique CharField of max_length 255
    value -- SerializableField by default could be used to store bool, int,
             float, str, list, dict and date
    """

    key = models.CharField(max_length=255, unique=True)
    value = SerializableField(blank=True, null=True)

    def __unicode__(self):
        return 'KVModel instance: ' + self.key + ' = ' + unicode(self.value)

    @classmethod
    def get_by_key(cls, key):
        """
        A static method that returns a KVModel instance.

        key -- unique key that is used for the search.
        this method will throw a DoesNotExist exception if an object with the
        key provided is not found.
        """
        return cls.objects.get(key=key)

    class Meta:
        abstract = True
