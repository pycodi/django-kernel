
class KernelSerializerModel(object):

    @classmethod
    def serializer_data(cls):
        return [f.name for f in cls._meta.get_fields() if not f.related_model]

    @classmethod
    def serializer_class(cls):
        """
        class Serializer(serializers.ModelSerializer):
            class Meta:
                model = cls
                fields = cls.serializer_data()
        return Serializer
        """

        class Serializer(serializers.ModelSerializer):
            class Meta:
                model = cls
                fields = cls.serializer_data()

        return Serializer

    @classmethod
    def serializer_class_list(cls):
        return cls.serializer_class()

    @classmethod
    def serializer_viewsets(cls):
        from kernel.rest import viewsets as rv
        from rest_framework.decorators import detail_route, list_route
        from rest_framework.response import Response

        class ViewSet(rv.KernelViewSets):
            queryset = cls.objects.all()
            serializer_class = cls.get_serializer_class()
            filter_class = cls.get_filter_class()
            list_serializer_class = cls.get_list_serializer_class()

        return ViewSet