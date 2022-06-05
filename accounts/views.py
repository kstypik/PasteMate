from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views.generic import UpdateView

from .forms import ProfileForm


class ProfileUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    form_class = ProfileForm
    template_name = "account/profile_edit.html"
    success_message = "Your profile has been updated!"
    success_url = reverse_lazy("accounts:profile_update")

    def get_object(self, queryset=None):
        return self.request.user
