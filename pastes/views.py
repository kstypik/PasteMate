import copy

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
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
from django.views.generic.base import TemplateResponseMixin
from django.views.generic.detail import SingleObjectMixin
from pygments import lexers

from .forms import PasswordProtectedPasteForm, PasteForm, ReportForm
from .models import Folder, Paste, Report

User = get_user_model()


class AuthenticatedUserInFormKwargsMixin:
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.request.user.is_authenticated:
            kwargs.update({"user": self.request.user})
        return kwargs


class PastePublicOrIsAuthorMixin:
    def get_object(self, queryset=None):
        object = super().get_object()
        if object.exposure == Paste.Exposure.PRIVATE:
            if object.author == self.request.user:
                return object
            raise Http404

        return object


class EnsureStandardPasteMixin(PastePublicOrIsAuthorMixin):
    def get_object(self):
        object = super().get_object()
        if object.password or object.burn_after_read:
            raise Http404
        return object


class PasteCreateView(AuthenticatedUserInFormKwargsMixin, CreateView):
    model = Paste
    form_class = PasteForm
    template_name = "pastes/form.html"
    extra_context = {
        "action_type": "Create New Paste",
    }

    def form_valid(self, form):
        if (
            not form.cleaned_data["post_anonymously"]
            and self.request.user.is_authenticated
        ):
            form.instance.author = self.request.user
        return super().form_valid(form)


class ClonedGetObjectMixin:
    def get_object(self):
        object = get_object_or_404(Paste, uuid=self.kwargs["uuid"])
        return object


class PasteCloneView(
    LoginRequiredMixin, EnsureStandardPasteMixin, ClonedGetObjectMixin, PasteCreateView
):
    extra_context = {
        "action_type": "Clone",
    }

    def get_initial(self):
        cloned_paste = self.get_object()
        return {
            "content": cloned_paste.content,
            "syntax": cloned_paste.syntax,
            "title": cloned_paste.title,
        }


class PasteInstanceMixin:
    model = Paste
    slug_field = "uuid"
    slug_url_kwarg = "uuid"
    context_object_name = "paste"


class PasteDetailView(PasteInstanceMixin, PastePublicOrIsAuthorMixin, DetailView):
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


class RawPasteDetailView(
    PasteInstanceMixin, EnsureStandardPasteMixin, SingleObjectMixin, View
):
    def get(self, request, *args, **kwargs):
        object = self.get_object()
        return HttpResponse(object.content, content_type="text/plain")


class DownloadPasteView(
    PasteInstanceMixin, EnsureStandardPasteMixin, SingleObjectMixin, View
):
    def get(self, request, *args, **kwargs):
        object = self.get_object()
        response = HttpResponse(object.content, content_type="text/plain")
        lexer = lexers.get_lexer_by_name(object.syntax)
        try:
            ext = lexer.filenames[0].split("*")[1]
        except:
            ext = ""
        response[
            "Content-Disposition"
        ] = f'attachment; filename="paste-{object.uuid}{ext}'
        return response


class PasteDetailWithPasswordView(
    PasteInstanceMixin, PastePublicOrIsAuthorMixin, DetailView
):
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


class UserListMixin:
    context_object_name = "pastes"
    template_name = "pastes/user_list.html"
    paginate_by = settings.PASTES_USER_LIST_PAGINATE_BY


class UserPasteListView(UserListMixin, ListView):
    def get_queryset(self):
        self.user = get_object_or_404(User, username=self.kwargs["username"])
        if self.request.user == self.user:
            return Paste.objects.filter(author=self.user, folder=None)
        return Paste.published.filter(author=self.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["author"] = self.user
        if self.request.user == self.user:
            context["folders"] = Folder.objects.filter(created_by=self.request.user)
        return context


class UserFolderListView(UserListMixin, ListView):
    def get_queryset(self):
        self.folder = get_object_or_404(
            Folder, created_by=self.request.user, name=self.kwargs["folder_slug"]
        )
        return self.folder.pastes.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["folder"] = self.folder
        context["author"] = self.request.user
        return context


class PasteArchiveListView(ListView):
    context_object_name = "pastes"
    template_name = "pastes/archive.html"

    def get_queryset(self):
        syntax = self.kwargs.get("syntax")
        if syntax:
            return Paste.published.filter(syntax=self.kwargs["syntax"])
        return Paste.published.all()[: settings.PASTES_ARCHIVE_LENGTH]


class EmbedPasteView(PasteInstanceMixin, EnsureStandardPasteMixin, DetailView):
    template_name = "pastes/embed.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context["direct_embed_link"] = (
            self.request.get_host() + self.object.embeddable_image.url
        )
        return context


class PrintPasteView(
    PasteInstanceMixin,
    EnsureStandardPasteMixin,
    TemplateResponseMixin,
    SingleObjectMixin,
    View,
):
    template_name = "pastes/print.html"

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data()
        return self.render_to_response(context)


class ReportPasteView(SuccessMessageMixin, CreateView):
    model = Report
    form_class = ReportForm
    template_name = "pastes/report.html"
    success_message = "Your report was submitted and is awaiting for moderation."

    def dispatch(self, request, *args, **kwargs):
        self.paste_object = get_object_or_404(Paste, uuid=self.kwargs["uuid"])
        if (
            self.paste_object.password
            or self.paste_object.burn_after_read
            or self.paste_object.author == request.user
        ):
            raise Http404
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["reported_paste"] = self.paste_object
        return context

    def form_valid(self, form):
        form.instance.paste = self.paste_object
        return super().form_valid(form)

    def get_success_url(self):
        return self.paste_object.get_absolute_url()
