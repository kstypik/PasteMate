from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views.generic import DeleteView, UpdateView

from .forms import AccountDeleteForm, ProfileForm

User = get_user_model()


class ProfileUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    form_class = ProfileForm
    template_name = "account/profile_edit.html"
    success_message = "Your profile has been updated!"
    success_url = reverse_lazy("accounts:profile_update")

    def get_object(self, queryset=None):
        return self.request.user


class AccountDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = User
    form_class = AccountDeleteForm
    template_name = "account/account_delete.html"
    success_message = "Your account has been deleted."
    success_url = reverse_lazy("pastes:create")

    def get_object(self, queryset=None):
        return self.request.user

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request
        return kwargs
