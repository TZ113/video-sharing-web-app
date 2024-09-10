from allauth.socialaccount.models import SocialAccount
from django import forms
from django.contrib.auth.forms import (
    PasswordChangeForm,
    UserChangeForm,
    UserCreationForm,
)
from django.utils.translation import gettext_lazy as _

from .models import User, UserProfile


class CustomPasswordChangeForm(PasswordChangeForm):
    """Modifying the PasswordChangeForm to handle password reset for social login accounts"""

    def clean_old_password(self):
        """Checks whether an user was created by social login, but still hasn't set a password,
        returns None in that case"""
        if (
            self.user.socialaccount_set.filter().exists()  # type: ignore
            and not self.user.has_usable_password()
        ):
            return None
        return super().clean_old_password()


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["username", "email"]


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ["username", "email", "password"]


class UsernameChangeForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            "username",
        ]


class EmailChangeForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            "email",
        ]


class AboutForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(AboutForm, self).__init__(*args, **kwargs)
        self.fields["about"].required = True

    class Meta:
        model = UserProfile
        fields = [
            "about",
        ]
