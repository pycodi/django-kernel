from __future__ import unicode_literals
import warnings

from django.conf import settings
from django.contrib.auth import get_user_model, REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import (SetPasswordForm,
                                       PasswordChangeForm, PasswordResetForm)
from django.contrib.auth.tokens import default_token_generator
from django.contrib import auth
from django.core.exceptions import PermissionDenied

try:
    from django.contrib.sites.shortcuts import get_current_site
except ImportError:
    from django.contrib.sites.models import get_current_site  # Django < 1.7
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import redirect, resolve_url
from django.utils.functional import lazy
from django.utils.http import base36_to_int, is_safe_url
from django.utils import six
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic import FormView, TemplateView, RedirectView


try:
    from django.contrib.auth import update_session_auth_hash
except ImportError:
    # Django < 1.7
    def update_session_auth_hash(request, user):
        pass


def _safe_resolve_url(url):
    return six.text_type(resolve_url(url))


resolve_url_lazy = lazy(_safe_resolve_url, six.text_type)


class WithCurrentSiteMixin(object):
    def get_current_site(self):
        return get_current_site(self.request)

    def get_context_data(self, **kwargs):
        kwargs = super(WithCurrentSiteMixin, self).get_context_data(**kwargs)
        current_site = self.get_current_site()
        kwargs.update({
            'site': current_site,
            'site_name': current_site.name,
        })
        return kwargs


class WithNextUrlMixin(object):
    redirect_field_name = REDIRECT_FIELD_NAME
    success_url = None

    def get_next_url(self):
        request = self.request
        redirect_to = request.POST.get(self.redirect_field_name,
                                       request.GET.get(self.redirect_field_name, ''))
        if not redirect_to:
            return

        if is_safe_url(redirect_to, host=self.request.get_host()):
            return redirect_to

    def get_success_url(self):
        return self.get_next_url() or super(WithNextUrlMixin, self).get_success_url()

    def get_redirect_url(self, **kwargs):
        return self.get_next_url() or super(WithNextUrlMixin, self).get_redirect_url(**kwargs)


def DecoratorMixin(decorator):
    """
    Converts a decorator written for a function view into a mixin for a
    class-based view.
    ::
        LoginRequiredMixin = DecoratorMixin(login_required)
        class MyView(LoginRequiredMixin):
            pass
        class SomeView(DecoratorMixin(some_decorator),
                       DecoratorMixin(something_else)):
            pass
    """

    class Mixin(object):
        __doc__ = decorator.__doc__

        @classmethod
        def as_view(cls, *args, **kwargs):
            view = super(Mixin, cls).as_view(*args, **kwargs)
            return decorator(view)

    Mixin.__name__ = str('DecoratorMixin(%s)' % decorator.__name__)
    return Mixin


NeverCacheMixin = DecoratorMixin(never_cache)
CsrfProtectMixin = DecoratorMixin(csrf_protect)
LoginRequiredMixin = DecoratorMixin(login_required)
SensitivePostParametersMixin = DecoratorMixin(sensitive_post_parameters('password', 'old_password', 'password1', 'password2', 'new_password1', 'new_password2'))


class AuthDecoratorsMixin(NeverCacheMixin, CsrfProtectMixin, SensitivePostParametersMixin):
    pass


class KernelDispachMixin(object):
    can_action = False

    def dispatch(self, request, *args, **kwargs):
        if self.can_action:
            if not self.can_action(request):
                if not request.user.is_authenticated():
                    return redirect(settings.LOGIN_URL)
                raise PermissionDenied
        return super(KernelDispachMixin, self).dispatch(request, *args, **kwargs)