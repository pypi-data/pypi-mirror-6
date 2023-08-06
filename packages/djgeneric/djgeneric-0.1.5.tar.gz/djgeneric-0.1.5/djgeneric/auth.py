from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import MultipleObjectsReturned
from django import forms


class EmailAuthBackend(object):
    """
    Email Authentication Backend

    Allows a user to sign in using an email/password pair rather than
    a username/password pair.
    """

    def authenticate(self, username=None, password=None):
        """ Authenticate a user based on email address as the user name. """
        try:
            user = User.objects.get(email=username)
            if user.check_password(password):
                return user
        except (User.DoesNotExist, MultipleObjectsReturned):
            return None

    def get_user(self, user_id):
        """ Get a User object from the user_id. """
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None


class IdAuthBackend(object):
    """
    Id Authentication Backend

    Allows a user to sign in using an id/password pair rather than
    a username/password pair.
    """

    def authenticate(self, username=None, password=None):
        """ Authenticate a user based on email address as the user name. """
        try:
            user_id = int(username)
        except ValueError:
            return None

        try:
            user = User.objects.get(pk=user_id)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        """ Get a User object from the user_id. """
        try:
            return User.objects.get(pk=user_id)
        except (User.DoesNotExist, MultipleObjectsReturned):
            return None


class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(label=_("Username or email address"),
                max_length=254)
