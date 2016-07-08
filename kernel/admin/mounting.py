from django.apps import apps
from django.contrib import admin
from django.contrib.admin.views import main
from django.conf import settings


main.EMPTY_CHANGELIST_VALUE = ' '

for app in settings.MY_APPS:
    for cls in [m for m in apps.get_app_config(app).get_models()]:
        if hasattr(cls, 'ADMIN'):
            if cls.ADMIN:
                admin.site.register(cls, cls.get_admin_class())
