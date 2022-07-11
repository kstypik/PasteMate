from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views.generic import DeleteView, UpdateView

from pastemate.accounts.forms import (
    AccountDeleteForm,
    AvatarForm,
    PreferencesForm,
    ProfileForm,
)

User = get_user_model()


class AuthenticatedUserObjectMixin:
    def get_object(self, queryset=None):
        return self.request.user


class ProfileUpdateView(
    LoginRequiredMixin, SuccessMessageMixin, AuthenticatedUserObjectMixin, UpdateView
):
    form_class = ProfileForm
    template_name = "account/profile_edit.html"
    success_message = "Your profile has been updated!"
    success_url = reverse_lazy("accounts:profile_update")


class AvatarUpdateView(
    LoginRequiredMixin, SuccessMessageMixin, AuthenticatedUserObjectMixin, UpdateView
):
    form_class = AvatarForm
    template_name = "account/avatar_edit.html"
    success_message = "Your avatar has been set!"
    success_url = reverse_lazy("accounts:profile_update")


class AccountDeleteView(
    LoginRequiredMixin, SuccessMessageMixin, AuthenticatedUserObjectMixin, DeleteView
):
    model = User
    form_class = AccountDeleteForm
    template_name = "account/account_delete.html"
    success_message = "Your account has been deleted."
    success_url = reverse_lazy("pastes:create")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request
        return kwargs


class PreferencesUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    form_class = PreferencesForm
    template_name = "account/preferences.html"
    success_message = "Your preferences have been updated."
    success_url = reverse_lazy("accounts:preferences")

    def get_object(self, queryset=None):
        return self.request.user.preferences
