import copy

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
    View,
)
from django.views.generic.detail import SingleObjectMixin

from .forms import PasswordProtectedPasteForm, PasteForm
from .models import Paste

User = get_user_model()


class AuthenticatedUserInFormKwargsMixin:
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.request.user.is_authenticated:
            kwargs.update({"user": self.request.user})
        return kwargs


class PasteCreateView(AuthenticatedUserInFormKwargsMixin, CreateView):
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


class PasteDetailMixin:
    def get_object(self, queryset=None):
        object = super().get_object()
        if object.exposure == Paste.Exposure.PRIVATE:
            if object.author == self.request.user:
                return object
            raise Http404

        return object


class PasteDetailView(PasteInstanceMixin, PasteDetailMixin, DetailView):
    template_name = "pastes/detail.html"

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        if self.object.password:
            return redirect("pastes:detail_with_password", uuid=self.object.uuid)
        return response

    def post(self, request, *args, **kwargs):
        """For handling Burn After Read"""
        self.object = get_object_or_404(Paste, uuid=self.kwargs["uuid"])
        context = {"paste": self.object}
        self.object.burn_after_read = False
        self.object.delete()
        return self.render_to_response(context)

    def render_to_response(self, context, **response_kwargs):
        if self.object.burn_after_read:
            context["burn_after_read"] = True
        response = super().render_to_response(context, **response_kwargs)
        return response


class RawPasteDetailView(PasteInstanceMixin, PasteDetailMixin, SingleObjectMixin, View):
    def get_object(self):
        object = super().get_object()
        if object.password or object.burn_after_read:
            raise Http404
        return object

    def get(self, request, *args, **kwargs):
        object = self.get_object()
        return HttpResponse(object.content, content_type="text/plain")


class PasteDetailWithPasswordView(PasteInstanceMixin, PasteDetailMixin, DetailView):
    template_name = "pastes/detail.html"

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.password:
            context = self.get_context_data(object=self.object)
            context["password_protected"] = True
            context["password_form"] = PasswordProtectedPasteForm(
                correct_password=self.object.password
            )
            return self.render_to_response(context)
        else:
            return redirect(self.object)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.password:
            context = self.get_context_data(object=self.object)
            context["password_protected"] = True
            password_form = PasswordProtectedPasteForm(
                request.POST, correct_password=self.object.password
            )
            context["password_form"] = password_form
            if password_form.is_valid():
                context["password_correct"] = True
            return self.render_to_response(context)
        else:
            return redirect(self.object)


class PasteAuthorMixin:
    def get_object(self, queryset=None):
        object = super().get_object()
        if not object.author == self.request.user:
            raise Http404

        return object


class PasteUpdateView(
    AuthenticatedUserInFormKwargsMixin, PasteAuthorMixin, PasteInstanceMixin, UpdateView
):
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
    paginate_by = settings.PASTES_USER_LIST_PAGINATE_BY

    def get_queryset(self):
        self.user = get_object_or_404(User, username=self.kwargs["username"])
        if self.request.user == self.user:
            return Paste.objects.filter(author=self.user)
        return Paste.published.filter(author=self.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["author"] = self.user
        return context


class PasteArchiveListView(ListView):
    context_object_name = "pastes"
    template_name = "pastes/archive.html"

    def get_queryset(self):
        syntax = self.kwargs.get("syntax")
        if syntax:
            return Paste.published.filter(syntax=self.kwargs["syntax"])
        return Paste.published.all()[: settings.PASTES_ARCHIVE_LENGTH]
