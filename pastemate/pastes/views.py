from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.postgres.search import SearchVector
from django.db.models import Count
from django.http import Http404, HttpResponse, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.utils import timezone

from core.utils import count_hit, paginate
from pastes.forms import (
    FolderForm,
    PasswordProtectedPasteForm,
    PasteForm,
    ReportForm,
)
from pastes.models import Folder, Paste

User = get_user_model()


def create_paste(request):
    user = request.user if request.user.is_authenticated else None
    if request.method == "POST":
        form = PasteForm(data=request.POST, user=user)
        if form.is_valid():
            paste = form.save(commit=False)
            if (
                not form.cleaned_data.get("post_anonymously")
                and request.user.is_authenticated
            ):
                paste.author = request.user
            paste.save()

            return redirect(paste)
    else:
        form = PasteForm(user=user)

    return TemplateResponse(
        request, "pastes/form.html", {"action_type": "Create New Paste", "form": form}
    )


def clone_paste(request, paste_uuid):
    cloned_paste = get_object_or_404(Paste, uuid=paste_uuid)
    if (
        cloned_paste.is_private and not cloned_paste.is_author(request.user)
    ) or not cloned_paste.is_normally_accessible:
        raise Http404

    user = request.user if request.user.is_authenticated else None
    initial = {
        "content": cloned_paste.content,
        "syntax": cloned_paste.syntax,
        "title": cloned_paste.title,
    }
    if request.method == "POST":
        form = PasteForm(data=request.POST, initial=initial, user=user)
        if form.is_valid():
            paste = form.save(commit=False)
            if (
                not form.cleaned_data.get("post_anonymously")
                and request.user.is_authenticated
            ):
                paste.author = request.user
            paste.save()

            return redirect(paste)
    else:
        form = PasteForm(initial=initial, user=user)

    return TemplateResponse(
        request, "pastes/form.html", {"action_type": "Clone Paste", "form": form}
    )


def paste_detail(request, uuid):
    queryset = Paste.objects.all().select_related("folder", "author")
    paste = get_object_or_404(queryset, uuid=uuid)
    if paste.is_private and not paste.is_author(request.user):
        raise Http404

    context = {"paste": paste}

    if paste.password and request.user != paste.author:
        return redirect("pastes:detail_with_password", uuid=paste.uuid)

    hitcount = count_hit(request, paste)
    context["hitcount"] = hitcount

    if request.method == "POST":
        context["burned"] = True
        paste.burn_after_read = False
        paste.delete()

    return TemplateResponse(request, "pastes/detail.html", context=context)


def raw_paste_detail(request, uuid):
    queryset = Paste.objects.all().select_related("folder", "author")
    paste = get_object_or_404(queryset, uuid=uuid)
    if (
        paste.is_private and not paste.is_author(request.user)
    ) or not paste.is_normally_accessible:
        raise Http404
    return HttpResponse(paste.content, content_type="text/plain")


def download_paste(request, uuid):
    queryset = Paste.objects.all().select_related("folder", "author")
    paste = get_object_or_404(queryset, uuid=uuid)
    if (
        paste.is_private and not paste.is_author(request.user)
    ) or not paste.is_normally_accessible:
        raise Http404

    response = HttpResponse(paste.content, content_type="text/plain")
    response["Content-Disposition"] = f'attachment; filename="paste-{paste.uuid}.txt"'
    return response


def paste_detail_with_password(request, uuid):
    queryset = Paste.objects.all().select_related("folder", "author")
    paste = get_object_or_404(queryset, uuid=uuid)
    if paste.is_private and not paste.is_author(request.user):
        raise Http404

    context = {"paste": paste}

    if request.method == "POST":
        if paste.password:
            context["password_protected"] = True
            password_form = PasswordProtectedPasteForm(
                request.POST, correct_password=paste.password
            )
            context["password_form"] = password_form
            if password_form.is_valid():
                context["password_correct"] = True

                hitcount = count_hit(request, paste)
                context["hitcount"] = hitcount

                if paste.burn_after_read:
                    paste.delete()
        else:
            return redirect(paste)
    else:
        if paste.password:
            context["password_protected"] = True
            context["password_form"] = PasswordProtectedPasteForm(
                correct_password=paste.password
            )
        else:
            return redirect(paste)
    return TemplateResponse(request, "pastes/detail.html", context=context)


@login_required
def edit_paste(request, uuid):
    paste = get_object_or_404(Paste, uuid=uuid)
    if not paste.is_author(request.user):
        raise Http404

    user = request.user if request.user.is_authenticated else None
    if request.method == "POST":
        form = PasteForm(data=request.POST, instance=paste, user=user)
        if form.is_valid():
            paste = form.save(commit=False)
            paste.save()

            return redirect(paste)
    else:
        form = PasteForm(instance=paste, user=user)

    return TemplateResponse(
        request,
        "pastes/form.html",
        {
            "action_type": "Edit",
            "form": form,
            "paste": paste,
        },
    )


@login_required
def delete_paste(request, uuid):
    paste = get_object_or_404(Paste, uuid=uuid)
    if not paste.is_author(request.user):
        raise Http404
    if request.method == "POST":
        paste.delete()
        messages.success(request, "Paste was deleted successfully.")
        return redirect("/")
    return TemplateResponse(request, "pastes/delete.html", {"paste": paste})


def user_pastes(request, username):
    user = get_object_or_404(User, username=username)
    context = {"author": user}

    hitcount = count_hit(request, user)
    context["hitcount"] = hitcount

    display_as_guest = request.GET.get("guest") == "1"
    context["as_guest"] = display_as_guest

    if request.user != user or display_as_guest:
        pastes = Paste.public.filter(author=user)
    else:
        pastes = Paste.objects.filter(author=user, folder=None)

    page_num = request.GET.get("page", 1)
    context["page_obj"] = paginate(
        pastes, page_num, settings.PASTES_USER_LIST_PAGINATE_BY
    )

    if request.user == user and not display_as_guest:
        context["folders"] = (
            Folder.objects.filter(created_by=request.user)
            .annotate(num_pastes=Count("pastes"))
            .order_by("slug")
        )

        context["page_name"] = "my_pastes"
        context["stats"] = {
            "total_pastes": Paste.objects.filter(author=request.user).count(),
            "public_pastes": Paste.public.filter(author=request.user).count(),
            "unlisted_pastes": Paste.objects.filter(
                author=request.user, exposure=Paste.Exposure.UNLISTED
            ).count(),
            "private_pastes": Paste.objects.filter(
                author=request.user, exposure=Paste.Exposure.PRIVATE
            ).count(),
        }

    return TemplateResponse(request, "pastes/user_list.html", context=context)


def search_pastes(request):
    query = request.GET.get("q", "")
    pastes = Paste.objects.annotate(search=SearchVector("content", "title")).filter(
        author=request.user, search=query
    )
    page_num = request.GET.get("page", 1)
    page_obj = paginate(pastes, page_num, settings.PASTES_USER_LIST_PAGINATE_BY)

    context = {"query": request.GET.get("q"), "page_obj": page_obj}

    return TemplateResponse(request, "pastes/search_results.html", context=context)


@login_required
def folder_detail(request, username, folder_slug):
    user = get_object_or_404(User, username=username)
    folder = get_object_or_404(Folder, created_by=request.user, slug=folder_slug)
    pastes = folder.pastes.all()
    page_num = request.GET.get("page", 1)
    page_obj = paginate(pastes, page_num, settings.PASTES_USER_LIST_PAGINATE_BY)

    context = {
        "page_obj": page_obj,
        "folder": folder,
        "author": user,
    }
    return TemplateResponse(request, "pastes/user_list.html", context=context)


@login_required
def edit_folder(request, username, folder_slug):
    get_object_or_404(User, username=username)
    folder = get_object_or_404(request.user.folders, slug=folder_slug)

    user = request.user if request.user.is_authenticated else None
    if request.method == "POST":
        form = FolderForm(data=request.POST, instance=folder, user=user)
        if form.is_valid():
            form.save()
            return redirect(folder)
    else:
        form = FolderForm(instance=folder, user=user)

    return TemplateResponse(
        request, "pastes/folder_form.html", context={"folder": folder, "form": form}
    )


@login_required
def delete_folder(request, username, folder_slug):
    user = get_object_or_404(User, username=username)
    folder = get_object_or_404(request.user.folders, slug=folder_slug)

    if request.method == "POST":
        folder.delete()
        messages.success(request, "Folder has been deleted.")
        return redirect(user)

    return TemplateResponse(request, "pastes/folder_delete.html", {"folder": folder})


def archive(request, syntax=None):
    if syntax:
        pastes = Paste.public.filter(syntax=syntax)[: settings.PASTES_ARCHIVE_LENGTH]
    else:
        pastes = Paste.public.all()[: settings.PASTES_ARCHIVE_LENGTH]

    context = {
        "pastes": pastes,
        "syntax": Paste.get_full_language_name(syntax),
        "page_name": "archive",
    }
    return TemplateResponse(request, "pastes/archive.html", context=context)


def embed_paste(request, uuid):
    paste = get_object_or_404(Paste, uuid=uuid)

    if paste.is_private or not paste.is_normally_accessible:
        raise Http404

    context = {
        "paste": paste,
    }

    if paste.embeddable_image:
        context["direct_embed_link"] = request.build_absolute_uri(
            paste.embeddable_image.url
        )

    return TemplateResponse(request, "pastes/embed.html", context)


def print_paste(request, uuid):
    paste = get_object_or_404(Paste, uuid=uuid)
    if (
        paste.is_private and not paste.is_author(request.user)
    ) or not paste.is_normally_accessible:
        raise Http404

    return TemplateResponse(request, "pastes/print.html", {"paste": paste})


def report_paste(request, uuid):
    reported_paste = get_object_or_404(Paste, uuid=uuid)
    if (
        not reported_paste.is_normally_accessible
        or reported_paste.is_author(request.user)
        or reported_paste.is_private
    ):
        raise Http404

    if request.method == "POST":
        form = ReportForm(data=request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.paste = reported_paste
            report.save()
            messages.success(
                request, "Your report was submitted and is awaiting for moderation."
            )
            return redirect(reported_paste)
    else:
        form = ReportForm()

    return TemplateResponse(
        request, "pastes/report.html", {"form": form, "reported_paste": reported_paste}
    )


def syntax_languages(request):
    return TemplateResponse(
        request,
        "pastes/syntax_languages.html",
        {"languages": Paste.public.languages(), "page_name": "languages"},
    )


@login_required
def backup_pastes(request):
    if request.method == "POST":
        response = HttpResponse(content_type="application/zip")

        Paste.make_backup_archive(response, request.user)
        date_str = timezone.now().strftime("%Y%m%d")
        archive_name = f"pastemate_backup_{date_str}.zip"

        response["Content-Disposition"] = f"attachment; filename={archive_name}"
        return response
    return HttpResponseNotAllowed(["POST"])
