from django.db import models
from django.utils import six
from kicker.views import models_list
from kicker.broker import send_message
from rest_framework import serializers
from rest_framework.renderers import JSONRenderer
import time

class DefaultManager(models.Manager):
    def get_queryset(self):
        return super(DefaultManager, self).get_queryset().filter(is_active=True)

    def get_all(self):
        return super(DefaultManager, self).get_queryset()

def custom_delete(obj):
    obj.is_active = False
    return obj.save()

def update_timestamp(function):
    def wrapper(*args, **kwargs):
        args[0].timestamp = time.time()
        return function(*args, **kwargs)
    return wrapper

def inform_broker(function):
    def wrapper(*args, **kwargs):
        prop = function(*args, **kwargs)
        send_message(args[0].__class__.__name__, args[0].serialize())
        return prop
    return wrapper


def create_default_serializer(cls):

    class Meta:
        model = cls

    serializer_class = type(cls.__name__ + '_serializer', 
        (serializers.ModelSerializer,), {'Meta': Meta})

    cls.serializer_class = serializer_class
    
    return lambda self: JSONRenderer().render(serializer_class(self).data)

class DiffTrackerMeta(models.base.ModelBase):

    def __new__(cls, name, bases, attrs):
        if name not in ['NewBase', 'DiffTracker']:
            attrs['timestamp'] = models.FloatField(blank=True, null=True)
            attrs['is_active'] = models.BooleanField(default=True)
            attrs['objects'] = DefaultManager()
        prop = super(DiffTrackerMeta, cls).__new__(cls, name, bases, attrs)
        if not attrs.get('serialize'):
            prop.serialize = create_default_serializer(prop)
        if name not in ['NewBase', 'DiffTracker']:
            prop.save = update_timestamp(inform_broker(prop.save))
            models_list[name] = {'model': prop}
            prop.delete = custom_delete
        return prop

class DiffTracker(six.with_metaclass(DiffTrackerMeta, models.Model)):

    def save(self, *args, **kwargs):
        return super(DiffTracker, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        return self.save(*args, **kwargs)

    class Meta:
        abstract = True
