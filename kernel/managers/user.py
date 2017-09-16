from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager, PermissionsMixin)
from django.utils import timezone
from polymorphic.models import PolymorphicManager


class EmailUserMixinManager(PolymorphicManager, BaseUserManager):
    """
    Custom manager for EmailUser.
    """

    def _create_user(self, email, password, is_staff, is_superuser, **extra_fields):
        """
        Create and save an EmailUser with the given email and password.
        :param str email: user email
        :param str password: user password
        :param bool is_staff: whether user staff or not
        :param bool is_superuser: whether user admin or not
        :return custom_user.models.EmailUser user: user
        :raise ValueError: email is not set
        """
        now = timezone.now()
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        is_active = extra_fields.pop("is_active", True)
        user = self.model(email=email, is_staff=is_staff, is_active=is_active,
                          is_superuser=is_superuser, last_login=now,
                          date_joined=now, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """
        Create and save an EmailUser with the given email and password.
        :param str email: user email
        :param str password: user password
        :return custom_user.models.EmailUser user: regular user
        """
        is_staff = extra_fields.pop("is_staff", False)
        return self._create_user(email, password, is_staff, False, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and save an EmailUser with the given email and password.
        :param str email: user email
        :param str password: user password
        :return custom_user.models.EmailUser user: admin user
        """
        return self._create_user(email, password, True, True, **extra_fields)
