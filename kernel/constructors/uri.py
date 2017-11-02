from django.conf.urls import url


class KernelUriModel(object):

    URI = 'pk'
    URI_FORMAT_DETAIL = None
    ALIAS = False

    @classmethod
    def get_alias(cls):
        if cls.ALIAS:
            return cls.ALIAS
        return str(cls.__name__).lower()

    @classmethod
    def get_uri_create(cls):
        from django.conf.urls import url
        fields = cls.list_fields()
        return url(r'^%s/new.html$' % cls.get_alias(),
                   cls.get_create_view_class().as_view(), name='{0}_create'.format(str(cls.__name__).lower()))

    @classmethod
    def get_uri_update(cls):
        return url(r'^%s/(?P<pk>\d+)/edit/$' % cls.get_alias(),
                   cls.get_update_view_class().as_view(), name='{0}_update'.format(str(cls.__name__).lower()))

    @classmethod
    def get_uri_delete(cls):
        return url(r'^%s/(?P<pk>\d+)/delete/' % cls.get_alias(),
                   cls.get_delete_view_class().as_view(), name='{0}_delete'.format(str(cls.__name__).lower()))

    @classmethod
    def get_uri_detail(cls, pk: str = URI, format: str = '.html'):
        return url(r'^%s/(?P<%s>[a-zA-Z0-9_A-Яа-я-]{1,300})%s$' %
                   (cls.get_alias(), cls.URI,(cls.URI_FORMAT_DETAIL if cls.URI_FORMAT_DETAIL else format)),
                   cls.get_detail_view_class().as_view(), name='{0}_view'.format(str(cls.__name__).lower()))

    @classmethod
    def get_uri_list(cls):
        return url(r'^%s/$' % cls.get_alias().lower(),
                   cls.get_list_view_class().as_view(), name='{0}_list'.format(str(cls.__name__).lower()))

    @classmethod
    def get_uri_export(cls):
        return url(r'^%s/export/' % cls.get_alias(),
                   cls.get_export_view_class().as_view(), name='{0}_export'.format(str(cls.__name__).lower()))

    @classmethod
    def get_uri_detail_export(cls):
        return url(r'^%s/(?P<pk>\d+)/export/' % cls.get_alias(),
                   cls.get_detail_export_view_class().as_view(),
                   name='{0}_detail_export'.format(str(cls.__name__).lower()))

    @classmethod
    def get_uri_crud(cls):
        import re
        uri_list = []
        for m in cls.methods():
            if re.match('get_uri_', m) and not m == 'get_uri_crud':
                uri_list.append(getattr(cls, m)())
        return uri_list