from rest_framework import serializers
from django.contrib.sites.models import Site
from kernel.middleware import CrequestMiddleware

import socket

class StdImageFieldSerializer(serializers.ImageField):

    def to_native(self, obj):
        return self.get_variations_urls(obj)

    def to_representation(self, obj):
        return self.get_variations_urls(obj)

    def get_variations_urls(self, obj):
        return_object = {}
        field = obj.field
        if hasattr(field, 'variations'):
            variations = field.variations
            for key in variations.keys():
                if hasattr(obj, key):
                    field_obj = getattr(obj, key, None)
                    if field_obj and hasattr(field_obj, 'url'):
                        return_object[key] = '{0}{1}'.format(Site.objects.get_current(), field_obj.url)
        return return_object
