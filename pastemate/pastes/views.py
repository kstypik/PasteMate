from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.postgres.search import SearchVector
from django.db.models import Count
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    TemplateView,
    UpdateView,
    View,
)
from django.views.generic.base import TemplateResponseMixin
from django.views.generic.detail import SingleObjectMixin
from hitcount.models import HitCount
from hitcount.views import HitCountDetailView, HitCountMixin

from .forms import FolderForm, PasswordProtectedPasteForm, PasteForm, ReportForm
from .models import Folder, Paste, Report

User = get_user_model()


class AuthenticatedUserInFormKwargsMixin:
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.request.user.is_authenticated:
            kwargs.update({"user": self.request.user})
        return kwargs


class PasteNonPrivateOrUserIsAuthorMixin:
    def get_object(self):
        object = super().get_object()
        if object.is_private and not object.is_author(self.request.user):
            raise Http404
        return object


class NormallyAccessiblePasteMixin(PasteNonPrivateOrUserIsAuthorMixin):
    def get_object(self):
        object = super().get_object()
        if not object.is_normally_accessible:
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
            not form.cleaned_data.get("post_anonymously")
            and self.request.user.is_authenticated
        ):
            form.instance.author = self.request.user
        return super().form_valid(form)


class PasteCloneView(LoginRequiredMixin, NormallyAccessiblePasteMixin, PasteCreateView):
    extra_context = {
        "action_type": "Clone Paste",
    }

    def get_object(self):
        object = get_object_or_404(Paste, uuid=self.kwargs["uuid"])
        return object

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


class PasteDetailView(
    PasteInstanceMixin, PasteNonPrivateOrUserIsAuthorMixin, HitCountDetailView
):
    template_name = "pastes/detail.html"
    count_hit = True

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.password and request.user != obj.author:
            return redirect("pastes:detail_with_password", uuid=obj.uuid)

        return super().dispatch(request, *args, **kwargs)

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
    PasteInstanceMixin, NormallyAccessiblePasteMixin, SingleObjectMixin, View
):
    def get(self, request, *args, **kwargs):
        object = self.get_object()
        return HttpResponse(object.content, content_type="text/plain")


class DownloadPasteView(
    PasteInstanceMixin, NormallyAccessiblePasteMixin, SingleObjectMixin, View
):
    def get(self, request, *args, **kwargs):
        object = self.get_object()
        response = HttpResponse(object.content, content_type="text/plain")
        response[
            "Content-Disposition"
        ] = f'attachment; filename="paste-{object.uuid}.txt"'
        return response


class PasteDetailWithPasswordView(
    PasteInstanceMixin, PasteNonPrivateOrUserIsAuthorMixin, DetailView
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
                if self.object.burn_after_read:
                    self.object.delete()
            return self.render_to_response(context)
        else:
            return redirect(self.object)


class PasteAuthorMixin:
    def get_object(self, queryset=None):
        object = super().get_object()
        if not object.is_author(self.request.user):
            raise Http404

        return object


class PasteUpdateView(
    LoginRequiredMixin,
    AuthenticatedUserInFormKwargsMixin,
    PasteAuthorMixin,
    PasteInstanceMixin,
    UpdateView,
):
    form_class = PasteForm
    template_name = "pastes/form.html"
    extra_context = {
        "action_type": "Edit",
    }


class PasteDeleteView(
    LoginRequiredMixin, PasteAuthorMixin, PasteInstanceMixin, DeleteView
):
    success_url = "/"
    template_name = "pastes/delete.html"


class UserListMixin:
    context_object_name = "pastes"
    template_name = "pastes/user_list.html"

    def get_paginate_by(self, queryset):
        return settings.PASTES_USER_LIST_PAGINATE_BY


class UserStatsMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        show_stats = context.pop("show_stats", None)
        if show_stats:
            context["stats"] = {
                "total_pastes": Paste.objects.filter(author=self.request.user).count(),
                "public_pastes": Paste.public.filter(author=self.request.user).count(),
                "unlisted_pastes": Paste.objects.filter(
                    author=self.request.user, exposure=Paste.Exposure.UNLISTED
                ).count(),
                "private_pastes": Paste.objects.filter(
                    author=self.request.user, exposure=Paste.Exposure.PRIVATE
                ).count(),
            }
        return context


class UserPasteListView(UserStatsMixin, UserListMixin, ListView, HitCountMixin):
    def display_as_guest(self):
        if self.request.GET.get("guest") == "1":
            return True
        return False

    def get_queryset(self):
        self.user = get_object_or_404(User, username=self.kwargs["username"])

        if self.request.user != self.user or self.display_as_guest():
            return Paste.public.filter(author=self.user)
        return Paste.objects.filter(author=self.user, folder=None)

    def get_context_data(self, **kwargs):
        show_stats = True if self.request.user == self.user else False
        context = super().get_context_data(show_stats=show_stats, **kwargs)
        context["author"] = self.user

        hit_count = HitCount.objects.get_for_object(self.user)
        hits = hit_count.hits

        hit_count_response = self.hit_count(self.request, hit_count)
        if hit_count_response.hit_counted:
            hits = hits + 1
        context["total_hits"] = hits

        if self.request.user == self.user and not self.display_as_guest():
            context["folders"] = (
                Folder.objects.filter(created_by=self.request.user)
                .annotate(num_pastes=Count("pastes"))
                .order_by("slug")
            )

        context["as_guest"] = self.display_as_guest()
        return context


class SearchResultsView(LoginRequiredMixin, ListView):
    context_object_name = "pastes"
    template_name = "pastes/search_results.html"
    paginate_by = settings.PASTES_USER_LIST_PAGINATE_BY

    def get_queryset(self):
        query = self.request.GET.get("q", "")
        return Paste.objects.annotate(search=SearchVector("content", "title")).filter(
            author=self.request.user, search=query
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["query"] = self.request.GET.get("q")
        return context


class UserFolderListView(LoginRequiredMixin, UserStatsMixin, UserListMixin, ListView):
    def get_queryset(self):
        self.user = get_object_or_404(User, username=self.kwargs["username"])
        self.folder = get_object_or_404(
            Folder, created_by=self.request.user, slug=self.kwargs["folder_slug"]
        )
        return self.folder.pastes.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(show_stats=True, **kwargs)
        context["folder"] = self.folder
        context["author"] = self.request.user
        return context


class UserFolderUpdateView(
    LoginRequiredMixin,
    SuccessMessageMixin,
    AuthenticatedUserInFormKwargsMixin,
    UpdateView,
):
    slug_url_kwarg = "folder_slug"
    form_class = FolderForm
    context_object_name = "folder"
    success_message = 'Folder "%(name)s" has been updated.'
    template_name = "pastes/folder_form.html"

    def get_queryset(self):
        return Folder.objects.filter(created_by=self.request.user)

    def get_success_url(self):
        return reverse(
            "pastes:user_folder",
            kwargs={
                "username": self.request.user.username,
                "folder_slug": self.object.slug,
            },
        )


class UserFolderDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    slug_url_kwarg = "folder_slug"
    context_object_name = "folder"
    template_name = "pastes/folder_delete.html"
    success_message = "Folder has been deleted."

    def get_queryset(self):
        return Folder.objects.filter(created_by=self.request.user)

    def get_success_url(self):
        return reverse(
            "pastes:user_pastes",
            kwargs={
                "username": self.request.user.username,
            },
        )


class PasteArchiveListView(ListView):
    context_object_name = "pastes"
    template_name = "pastes/archive.html"

    def get_queryset(self):
        self.syntax = self.kwargs.get("syntax")
        if self.syntax:
            return Paste.public.filter(syntax=self.syntax)
        return Paste.public.all()[: settings.PASTES_ARCHIVE_LENGTH]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["syntax"] = Paste.get_full_language_name(self.syntax)
        return context


class EmbedPasteView(PasteInstanceMixin, NormallyAccessiblePasteMixin, DetailView):
    template_name = "pastes/embed.html"

    def get_object(self, queryset=None):
        obj = super().get_object()
        if obj.exposure == Paste.Exposure.PRIVATE:
            raise Http404
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context["direct_embed_link"] = (
            self.request.get_host() + self.object.embeddable_image.url
        )
        return context


class PrintPasteView(
    PasteInstanceMixin,
    NormallyAccessiblePasteMixin,
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
            or self.paste_object.exposure == Paste.Exposure.PRIVATE
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


class SyntaxLanguagesView(TemplateView):
    template_name = "pastes/syntax_languages.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["languages"] = (
            Paste.public.exclude(syntax="text")
            .order_by("syntax")
            .distinct()
            .values("syntax")
            .annotate(used=Count("syntax"))
        )
        return context


class BackupUserPastesView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        response = HttpResponse(content_type="application/zip")

        Paste.make_backup_archive(response, self.request.user)
        date_str = timezone.now().strftime("%Y%m%d")
        archive_name = f"pastemate_backup_{date_str}.zip"

        response["Content-Disposition"] = f"attachment; filename={archive_name}"
        return response
