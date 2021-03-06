from django.conf.urls import *
from django.conf import settings
from django.apps import apps
from django.contrib import admin

from kernel.views import login as kv
from kernel import models as km


urlpatterns = [
    url(r'^signup/$', kv.LoginView.as_view(), name='signup'),
    url(r'^login/$', kv.LoginView.as_view(), name='login'),
    url(r'^logout/$', kv.LogoutView.as_view(), name='logout'),
    url(r'^password/change/$', kv.PasswordChangeView.as_view(), name='password_change'),
    url(r'^password/change/done/$', kv.PasswordChangeDoneView.as_view(), name='password_change_done'),
    url(r'^password/reset/$', kv.PasswordResetView.as_view(), name='password_reset'),
    url(r'^password/reset/done/$', kv.PasswordResetDoneView.as_view(), name='password_reset_done'),
    url(r'^reset/done/$', kv.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    url(r'^reset/(?P<uidb36>[0-9A-Za-z]{1,13})-(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', kv.PasswordResetConfirmView.as_view()),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', kv.PasswordResetConfirmView.as_view(), name='password_reset_confirm')
]
#urlpatterns += km.KernelUser.urls()

