try:
    from django.conf.urls import *
except ImportError:  # django < 1.4
    from django.conf.urls.defaults import *


from kernel import views as kv
from kernel import models as km

urlpatterns = [
    url(r'^login/$', kv.LoginView.as_view(), name='login'),
    url(r'^logout/$', kv.LogoutView.as_view(), name='logout'),
]
uri_list = [
    km.KernelUser.urls()
]

for ulist in uri_list:
    for uri in ulist:
        urlpatterns.append(uri)