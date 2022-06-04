import copy

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
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
        if form.instance.burn_after_read:
            pass
        return super().form_valid(form)


class PasteInstanceMixin:
    model = Paste
    slug_field = "uuid"
    slug_url_kwarg = "uuid"
    context_object_name = "paste"


class PasteDetailView(PasteInstanceMixin, DetailView):
    template_name = "pastes/detail.html"

    def get_object(self, queryset=None):
        object = super().get_object()
        if object.exposure == Paste.Exposure.PRIVATE:
            if object.author == self.request.user:
                return object
            raise Http404

        return object

    def render_to_response(self, context, **response_kwargs):
        if self.object.burn_after_read:
            context["burn_after_read"] = True
        response = super().render_to_response(context, **response_kwargs)
        return response

    def post(self, request, *args, **kwargs):
        """For handling Burn After Read"""
        self.object = get_object_or_404(Paste, uuid=self.kwargs["uuid"])
        context = {"paste": self.object}
        self.object.burn_after_read = False
        self.object.delete()
        return self.render_to_response(context)


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
        if self.request.user == self.user:
            return Paste.objects.filter(author=self.user)
        return Paste.published.filter(author=self.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user"] = self.user
        return context


class PasteArchiveListView(ListView):
    context_object_name = "pastes"
    template_name = "pastes/archive.html"

    def get_queryset(self):
        return Paste.published.all()[: settings.PASTES_ARCHIVE_LENGTH]
