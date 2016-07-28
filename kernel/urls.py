try:
    from django.conf.urls import *
except ImportError:  # django < 1.4
    from django.conf.urls.defaults import *


from kernel import views as kv

urlpatterns = [
    url(r'^login/$', kv.LoginView.as_view(), name='login'),
   url(r'^logout/$', kv.LogoutView.as_view(), name='logout'),
]
