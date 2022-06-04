from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import get_object_or_404, render
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from .forms import PasteForm
from .models import Paste

User = get_user_model()


class PasteCreateView(CreateView):
    model = Paste
    form_class = PasteForm
    template_name = "pastes/form.html"
    extra_context = {
        "action_type": "Create New Paste",
    }

    def form_valid(self, form):
        if self.request.user.is_authenticated:
            form.instance.author = self.request.user
        return super().form_valid(form)


class PasteInstanceMixin:
    model = Paste
    slug_field = "uuid"
    slug_url_kwarg = "uuid"
    context_object_name = "paste"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = self.object.title if self.object.title else "Untitled"

        return context


class PasteDetailView(PasteInstanceMixin, DetailView):
    template_name = "pastes/detail.html"


class PasteAuthorMixin:
    def get_object(self, queryset=None):
        object = super().get_object()
        if not object.author == self.request.user:
            raise Http404

        return object


class PasteUpdateView(PasteAuthorMixin, PasteInstanceMixin, UpdateView):
    form_class = PasteForm
    template_name = "pastes/form.html"
    extra_context = {
        "action_type": "Edit",
    }


class PasteDeleteView(PasteAuthorMixin, PasteInstanceMixin, DeleteView):
    success_url = "/"
    template_name = "pastes/delete.html"


class UserPasteListView(ListView):
    context_object_name = "pastes"
    template_name = "pastes/user_list.html"

    def get_queryset(self):
        self.user = get_object_or_404(User, username=self.kwargs["username"])
        return Paste.objects.filter(author=self.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user"] = self.user
        return context


class PasteArchiveListView(ListView):
    context_object_name = "pastes"
    template_name = "pastes/archive.html"

    def get_queryset(self):
        return Paste.objects.all()[: settings.PASTES_ARCHIVE_LENGTH]
