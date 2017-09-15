from django.contrib.auth import get_user_model

from kernel.middleware import CrequestMiddleware


class KernelAuthBackend(object):

    def authenticate(self, username=None, password=None, **kwargs):
        UserModel = get_user_model()

        try:
            user = get_user_model().objects.get(email=username)
            CrequestMiddleware.set_user(user)
            return user
        except get_user_model().DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return get_user_model().objects.get(pk=user_id)
        except get_user_model().DoesNotExist:
            return None