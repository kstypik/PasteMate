import datetime
from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model
from django.test import override_settings
from django.urls import reverse
from django.utils import formats, timezone
from pytest_django.asserts import (
    assertContains,
    assertInHTML,
    assertNotContains,
    assertRedirects,
    assertTemplateUsed,
)

from pastemate.core.utils import login_redirect_url
from pastemate.pastes import forms
from pastemate.pastes.models import Folder, Paste, Report

pytestmark = pytest.mark.django_db

User = get_user_model()

PASTE_CREATE_URL = reverse("pastes:create")
PASTES_ARCHIVE_URL = reverse("pastes:archive")
LANGUAGES_URL = reverse("pastes:syntax_languages")
BACKUP_URL = reverse("pastes:backup")
SEARCH_URL = reverse("pastes:search")


@pytest.fixture
def create_paste_with_url(create_paste):
    def make_paste_with_url(viewname, **kwargs):
        paste = create_paste(**kwargs)
        url = reverse(viewname, args=[paste.uuid])
        return paste, url

    return make_paste_with_url


@pytest.fixture
def create_paste_with_copied_url(create_paste_with_url):
    def make_paste_with_copied_url(**kwargs):
        return create_paste_with_url(viewname="pastes:clone", **kwargs)

    return make_paste_with_copied_url


@pytest.fixture
def create_paste_with_detail_url(create_paste_with_url):
    def make_paste_with_detail_url(**kwargs):
        return create_paste_with_url(viewname="pastes:detail", **kwargs)

    return make_paste_with_detail_url


@pytest.fixture
def create_paste_with_detail_with_password_url(create_paste_with_url):
    def make_paste_with_detail_with_password_url(**kwargs):
        return create_paste_with_url(viewname="pastes:detail_with_password", **kwargs)

    return make_paste_with_detail_with_password_url


@pytest.fixture
def create_paste_with_update_url(create_paste_with_url):
    def make_paste_with_update_url(**kwargs):
        return create_paste_with_url(viewname="pastes:update", **kwargs)

    return make_paste_with_update_url


@pytest.fixture
def create_paste_with_delete_url(create_paste_with_url):
    def make_paste_with_delete_url(**kwargs):
        return create_paste_with_url(viewname="pastes:delete", **kwargs)

    return make_paste_with_delete_url


class TestPasteCreate:
    def test_template_name_correct(self, client):
        response = client.get(PASTE_CREATE_URL)

        assertTemplateUsed(response, "pastes/form.html")

    def test_form_class_correct(self, client):
        response = client.get(PASTE_CREATE_URL)

        assert isinstance(response.context["form"], forms.PasteForm)

    def test_action_type_in_template(self, client):
        action_type = "Create New Paste"

        response = client.get(PASTE_CREATE_URL)

        assertContains(response, action_type)

    @patch("hcaptcha_field.fields.hCaptchaField.validate", return_value=True)
    def test_success_url(self, mock, client):
        data = {
            "content": "Hello World!",
            "syntax": "text",
            "exposure": "PU",
            "h-captcha-response": "valid",
        }
        response = client.post(PASTE_CREATE_URL, data=data)
        paste = Paste.objects.first()

        assertRedirects(response, paste.get_absolute_url())

    @patch("hcaptcha_field.fields.hCaptchaField.validate", return_value=True)
    def test_guest_can_create_paste(self, mock, client):
        data = {
            "content": "Hello World!",
            "syntax": "text",
            "exposure": "PU",
            "h-captcha-response": "valid",
        }
        client.post(PASTE_CREATE_URL, data=data)
        paste = Paste.objects.first()

        assert Paste.objects.count() == 1
        assert paste.content == "Hello World!"
        assert paste.author is None

    def test_user_can_create_paste(self, auto_login_user):
        client, user = auto_login_user()

        data = {
            "content": "Hello World!",
            "syntax": "text",
            "exposure": "PU",
        }
        client.post(PASTE_CREATE_URL, data=data)
        paste = Paste.objects.first()

        assert Paste.objects.count() == 1
        assert paste.content == "Hello World!"
        assert paste.author == user


class TestPasteClone:
    def test_action_type_in_template(
        self, auto_login_user, create_paste_with_copied_url
    ):
        paste, url = create_paste_with_copied_url()
        client, user = auto_login_user()
        action_type = "Clone Paste"

        response = client.get(url)

        assertContains(response, action_type)

    def test_login_required(self, client, create_paste_with_copied_url):
        paste, url = create_paste_with_copied_url()

        response = client.get(url)

        assertRedirects(response, login_redirect_url(url))

    def test_correct_initial_data(self, auto_login_user, create_paste_with_copied_url):
        paste, url = create_paste_with_copied_url()
        client, user = auto_login_user()

        response = client.get(url)

        form = response.context["form"]
        assert form.initial["content"] == paste.content
        assert form.initial["syntax"] == paste.syntax
        assert form.initial["title"] == paste.title

    def test_can_clone_paste_with_default_data(
        self, auto_login_user, create_paste_with_copied_url
    ):
        paste, url = create_paste_with_copied_url()
        client, user = auto_login_user()

        data = {
            "content": paste.content,
            "title": paste.title,
            "syntax": paste.syntax,
            "exposure": "PU",
        }
        client.post(url, data=data)
        created_paste = Paste.objects.first()

        assert Paste.objects.count() == 2
        assert created_paste.content == paste.content
        assert created_paste.syntax == paste.syntax
        assert created_paste.title == paste.title

    def test_can_clone_paste_with_custom_data(
        self, auto_login_user, create_paste_with_copied_url
    ):
        cloned_paste, url = create_paste_with_copied_url()
        client, user = auto_login_user()

        data = {
            "title": "My Cloned Paste",
            "syntax": "python",
            "content": "print('Hello World')",
            "exposure": "PU",
        }
        client.post(url, data=data)
        created_paste = Paste.objects.first()

        assert Paste.objects.count() == 2
        assert created_paste.content == "print('Hello World')"
        assert created_paste.syntax == "python"
        assert created_paste.title == "My Cloned Paste"

    def test_cannot_clone_private_paste(
        self, auto_login_user, create_paste_with_copied_url
    ):
        private_paste, url = create_paste_with_copied_url(
            exposure=Paste.Exposure.PRIVATE
        )
        client, user = auto_login_user()

        response = client.get(url)

        assert response.status_code == 404


class TestPasteDetailView:
    def test_template_name_correct(self, create_paste_with_detail_url, client):
        paste, url = create_paste_with_detail_url()

        response = client.get(url)

        assertTemplateUsed(response, "pastes/detail.html")

    def test_redirects_pastes_with_passwords_to_appropriate_view(
        self, create_paste, client
    ):
        paste_with_pass = create_paste(password="pass")

        response = client.get(paste_with_pass.get_absolute_url())

        assertRedirects(
            response,
            reverse("pastes:detail_with_password", args=[paste_with_pass.uuid]),
        )

    def test_can_burn_paste(self, client, create_paste):
        burnable_paste = create_paste(burn_after_read=True)
        burnable_paste_uuid = burnable_paste.uuid

        client.post(burnable_paste.get_absolute_url())

        assert not Paste.objects.filter(uuid=burnable_paste_uuid).exists()

    def test_displays_private_message_to_author_url_for_logged(
        self, auto_login_user, create_paste_with_detail_url, create_user
    ):
        client, logged_user = auto_login_user()
        user = create_user()
        paste, url = create_paste_with_detail_url(author=user)

        response = client.get(url)

        pm_url = reverse("pinax_messages:message_user_create", args=[user.id])
        assertContains(response, pm_url)

    def test_does_not_display_private_message_to_author_url_for_themselves(
        self, client, user, create_paste
    ):
        paste_with_author = create_paste(author=user)

        response = client.get(paste_with_author.get_absolute_url())

        pm_url = reverse("pinax_messages:message_user_create", args=[user.id])
        assertNotContains(response, pm_url)

    def test_does_not_display_private_message_to_author_url_for_unlogged(
        self, client, user, create_paste_with_detail_url
    ):
        paste, url = create_paste_with_detail_url(author=user)

        response = client.get(url)

        pm_url = reverse("pinax_messages:message_user_create", args=[user.id])
        assertNotContains(response, pm_url)

    def test_displays_correct_expiration_date_when_set(
        self, create_paste_with_detail_url, client
    ):
        paste, url = create_paste_with_detail_url(expiration_symbol=Paste.TEN_MINUTES)

        response = client.get(url)

        expiration_date = formats.date_format(paste.expiration_date, "c")
        html = f'<span class="to-relative-datetime text-capitalize">{expiration_date}</span>'
        assertInHTML(html, response.content.decode("utf-8"))

    def test_displays_authors_location_when_set(
        self, client, create_paste_with_detail_url, user
    ):
        paste, url = create_paste_with_detail_url(author=user)

        response = client.get(url)

        assertContains(response, user.location)

    def test_displays_authors_website_when_set(
        self, client, user, create_paste_with_detail_url
    ):
        paste, url = create_paste_with_detail_url(author=user)

        response = client.get(url)

        assertContains(response, user.website)


class TestRawPasteDetail:
    def test_can_view_raw_paste_detail(self, create_paste, client):
        paste = create_paste()
        response = client.get(reverse("pastes:raw_detail", args=[paste.uuid]))

        assert response.content.decode("utf-8") == paste.content


class TestDownloadPaste:
    def test_can_download_paste(self, client, create_paste):
        paste = create_paste()

        response = client.get(reverse("pastes:paste_download", args=[paste.uuid]))

        assert (
            response.headers["Content-Disposition"]
            == f'attachment; filename="paste-{paste.uuid}.txt"'
        )
        assertContains(response, paste.content)


class TestPasteDetailWithPassword:
    def test_template_name_correct(
        self, client, create_paste_with_detail_with_password_url
    ):
        paste, url = create_paste_with_detail_with_password_url(password="pass123")
        response = client.get(url)

        assertTemplateUsed(response, "pastes/detail.html")

    def test_password_form_in_context(
        self, client, create_paste_with_detail_with_password_url
    ):
        paste, url = create_paste_with_detail_with_password_url(password="pass123")
        response = client.get(url)
        form = response.context["password_form"]

        assert isinstance(form, forms.PasswordProtectedPasteForm)

    def test_password_protected_in_context(
        self, client, create_paste_with_detail_with_password_url
    ):
        paste, url = create_paste_with_detail_with_password_url(password="pass123")
        response = client.get(url)

        assert response.context["password_protected"]

    def test_redirects_to_normal_detail_on_GET_when_paste_has_no_password(
        self, client, create_paste
    ):
        paste_without_pass = create_paste()

        response = client.get(
            reverse("pastes:detail_with_password", args=[paste_without_pass.uuid])
        )

        assertRedirects(response, paste_without_pass.get_absolute_url())

    def test_redirects_to_normal_detail_on_POST_when_paste_has_no_password(
        self, create_paste, client
    ):
        paste_without_pass = create_paste()

        response = client.post(
            reverse("pastes:detail_with_password", args=[paste_without_pass.uuid])
        )

        assertRedirects(response, paste_without_pass.get_absolute_url())

    def test_can_access_paste_when_submitted_password_correct(
        self, client, create_paste_with_detail_with_password_url
    ):
        paste, url = create_paste_with_detail_with_password_url(password="pass123")

        response = client.post(
            url,
            data={
                "password": "pass123",
            },
        )

        assert response.context["password_correct"]
        assertContains(response, paste.content)

    def test_cannot_access_paste_when_submitted_password_wrong(
        self, client, create_paste_with_detail_with_password_url
    ):
        paste, url = create_paste_with_detail_with_password_url(password="pass123")

        response = client.post(
            url,
            data={
                "password": "incorrect",
            },
        )

        assert not response.context.get("password_correct", False)
        assertNotContains(response, paste.content)

    def test_cannot_access_password_protected_paste_on_GET(
        self, client, create_paste_with_detail_with_password_url
    ):
        paste, url = create_paste_with_detail_with_password_url(password="pass")

        response = client.get(url)

        assertNotContains(response, paste.content)

    def test_can_burn_paste_when_also_password_protected(self, client, create_paste):
        burnable_paste_with_pass = create_paste(
            burn_after_read=True, password="pass123"
        )
        burnable_paste_uuid = burnable_paste_with_pass.uuid
        paste_url = reverse(
            "pastes:detail_with_password", args=[burnable_paste_with_pass.uuid]
        )

        client.post(paste_url, data={"password": "pass123"})

        assert not Paste.objects.filter(uuid=burnable_paste_uuid).exists()

    def test_cannot_burn_paste_with_password_when_wrong_password_provided(
        self, client, create_paste
    ):
        burnable_paste_with_pass = create_paste(
            burn_after_read=True, password="pass123"
        )
        burnable_paste_uuid = burnable_paste_with_pass.uuid
        paste_url = reverse(
            "pastes:detail_with_password", args=[burnable_paste_with_pass.uuid]
        )

        client.post(paste_url, data={"password": "wrong"})

        assert Paste.objects.filter(uuid=burnable_paste_uuid).exists()

    def test_cannot_burn_paste_with_password_on_GET(self, client, create_paste):
        burnable_paste_with_pass = create_paste(
            burn_after_read=True, password="pass123"
        )
        burnable_paste_uuid = burnable_paste_with_pass.uuid
        paste_url = reverse(
            "pastes:detail_with_password", args=[burnable_paste_with_pass.uuid]
        )

        client.get(paste_url)

        assert Paste.objects.filter(uuid=burnable_paste_uuid).exists()


class TestPasteUpdate:
    def test_template_name_correct(self, auto_login_user, create_paste_with_update_url):
        client, user = auto_login_user()
        paste, url = create_paste_with_update_url(author=user)

        response = client.get(url)

        assertTemplateUsed(response, "pastes/form.html")

    def test_form_in_context(self, auto_login_user, create_paste_with_update_url):
        client, user = auto_login_user()
        paste, url = create_paste_with_update_url(author=user)

        response = client.get(url)
        form = response.context["form"]

        assert isinstance(form, forms.PasteForm)

    def test_cannot_update_if_not_paste_author(
        self, client, create_user, create_paste_with_update_url
    ):
        another_user = create_user()
        client.force_login(another_user)
        paste, url = create_paste_with_update_url()

        response = client.get(url)

        assert response.status_code == 404

    def test_action_type_in_template(
        self, client, auto_login_user, create_paste_with_update_url
    ):
        client, user = auto_login_user()
        paste, url = create_paste_with_update_url(author=user)
        action_type = "Edit"

        response = client.get(url)

        assertContains(response, action_type)

    def test_can_update_paste(self, auto_login_user, create_paste_with_update_url):
        client, user = auto_login_user()
        paste, url = create_paste_with_update_url(author=user)
        data = {
            "content": "Hello Updated",
            "syntax": "html",
            "exposure": "PU",
        }

        client.post(url, data=data)
        paste.refresh_from_db()

        assert paste.content == "Hello Updated"
        assert paste.syntax == "html"

    def test_redirects_to_paste_after_successful_update(
        self, auto_login_user, create_paste_with_update_url
    ):
        client, user = auto_login_user()
        paste, url = create_paste_with_update_url(author=user)
        data = {
            "content": "Hello Updated",
            "syntax": "html",
            "exposure": "PU",
        }

        response = client.post(url, data=data)

        assertRedirects(response, paste.get_absolute_url())


class TestPasteDelete:
    def test_template_name_correct(self, auto_login_user, create_paste_with_delete_url):
        client, user = auto_login_user()
        paste, url = create_paste_with_delete_url(author=user)

        response = client.get(url)

        assertTemplateUsed(response, "pastes/delete.html")

    def test_cannot_delete_if_not_paste_author(
        self, create_user, user, client, create_paste_with_update_url
    ):
        paste, url = create_paste_with_update_url(author=user)
        another_user = create_user()
        client.force_login(another_user)

        response = client.get(url)

        assert response.status_code == 404

    def test_can_delete_paste(self, auto_login_user, create_paste_with_delete_url):
        client, user = auto_login_user()
        paste, url = create_paste_with_delete_url(author=user)

        client.post(url)

        assert Paste.objects.count() == 0

    def test_redirects_to_homepage_after_successful_delete(
        self, auto_login_user, create_paste_with_delete_url
    ):
        client, user = auto_login_user()
        paste, url = create_paste_with_delete_url(author=user)

        response = client.post(url)

        assertRedirects(response, "/")


class TestUserPasteList:
    def test_template_name_correct(self, auto_login_user):
        client, user = auto_login_user()

        response = client.get(reverse("pastes:user_pastes", args=[user.username]))

        assertTemplateUsed(response, "pastes/user_list.html")

    def test_user_can_see_their_own_pastes(self, auto_login_user, create_paste):
        client, user = auto_login_user()
        public_paste = create_paste(author=user, exposure=Paste.Exposure.PUBLIC)
        unlisted_paste = create_paste(author=user, exposure=Paste.Exposure.UNLISTED)
        private_paste = create_paste(author=user, exposure=Paste.Exposure.PRIVATE)

        response = client.get(reverse("pastes:user_pastes", args=[user.username]))

        assert public_paste in response.context["page_obj"]
        assert unlisted_paste in response.context["page_obj"]
        assert private_paste in response.context["page_obj"]

    def test_others_cannot_see_users_nonpublic_pastes(self, client, user, create_paste):
        public_paste = create_paste(author=user, exposure=Paste.Exposure.PUBLIC)
        unlisted_paste = create_paste(author=user, exposure=Paste.Exposure.UNLISTED)
        private_paste = create_paste(author=user, exposure=Paste.Exposure.PRIVATE)

        response = client.get(reverse("pastes:user_pastes", args=[user.username]))

        assert public_paste in response.context["page_obj"]
        assert unlisted_paste not in response.context["page_obj"]
        assert private_paste not in response.context["page_obj"]

    def test_user_can_see_their_list_as_guest(self, auto_login_user, create_paste):
        client, user = auto_login_user()
        public_paste = create_paste(author=user, exposure=Paste.Exposure.PUBLIC)
        unlisted_paste = create_paste(author=user, exposure=Paste.Exposure.UNLISTED)
        private_paste = create_paste(author=user, exposure=Paste.Exposure.PRIVATE)

        response = client.get(
            reverse("pastes:user_pastes", args=[user.username]), {"guest": "1"}
        )

        assert public_paste in response.context["page_obj"]
        assert unlisted_paste not in response.context["page_obj"]
        assert private_paste not in response.context["page_obj"]

    def test_user_can_see_their_folders_on_list(self, auto_login_user, create_folder):
        client, user = auto_login_user()
        folder1 = create_folder(name="Folder 1", created_by=user)
        folder2 = create_folder(name="Folder 2", created_by=user)

        response = client.get(reverse("pastes:user_pastes", args=[user.username]))

        assert folder1 in response.context["folders"]
        assert folder2 in response.context["folders"]

    def test_show_count_of_pastes_in_folder(
        self, auto_login_user, create_folder, create_paste
    ):
        client, user = auto_login_user()
        folder1 = create_folder(name="Folder 1", created_by=user)
        folder2 = create_folder(name="Folder 2", created_by=user)
        create_folder(name="Folder 3", created_by=user)
        create_paste(folder=folder1)
        create_paste(folder=folder1)
        create_paste(folder=folder2)

        response = client.get(reverse("pastes:user_pastes", args=[user.username]))

        assert response.context["folders"].get(name="Folder 1").num_pastes == 2
        assert response.context["folders"].get(name="Folder 2").num_pastes == 1
        assert response.context["folders"].get(name="Folder 3").num_pastes == 0

    def test_user_cannot_see_other_users_folders_on_list(
        self, create_folder, user, client, create_user
    ):
        folder1 = create_folder(name="Folder 1", created_by=user)
        folder2 = create_folder(name="Folder 2", created_by=user)
        another_user = create_user()
        client.force_login(another_user)

        response = client.get(
            reverse("pastes:user_pastes", args=[another_user.username])
        )

        assert folder1 not in response.context["folders"]
        assert folder2 not in response.context["folders"]

    @override_settings(PASTES_USER_LIST_PAGINATE_BY=2)
    def test_user_list_is_paginated(self, create_paste, auto_login_user):
        client, user = auto_login_user()
        for _ in range(10):
            create_paste(author=user)

        response = client.get(reverse("pastes:user_pastes", args=[user.username]))

        assert response.context["page_obj"].paginator.num_pages == 5

    def test_show_statistics(self, create_paste, auto_login_user):
        client, user = auto_login_user()
        for _ in range(2):
            create_paste(author=user, exposure="PU")
        for _ in range(4):
            create_paste(author=user, exposure="UN")
        for _ in range(3):
            create_paste(author=user, exposure="PR")

        response = client.get(reverse("pastes:user_pastes", args=[user.username]))

        stats = response.context["stats"]
        assert stats["total_pastes"] == 9
        assert stats["public_pastes"] == 2
        assert stats["unlisted_pastes"] == 4
        assert stats["private_pastes"] == 3

    def test_displays_correct_expiration_date_when_set(
        self, auto_login_user, create_paste
    ):
        client, user = auto_login_user()
        expiring_paste = create_paste(expiration_symbol=Paste.TEN_MINUTES, author=user)

        response = client.get(reverse("pastes:user_pastes", args=[user.username]))

        expiration_date = formats.date_format(expiring_paste.expiration_date, "c")
        html = f'<span class="to-relative-datetime">{expiration_date}</span>'
        assertInHTML(html, response.content.decode("utf-8"))

    def test_displays_authors_location_when_set(self, auto_login_user):
        client, user = auto_login_user()

        response = client.get(reverse("pastes:user_pastes", args=[user.username]))

        assertContains(response, user.location)

    def test_displays_authors_website_when_set(self, auto_login_user):
        client, user = auto_login_user()

        response = client.get(reverse("pastes:user_pastes", args=[user.username]))

        html = f'<a href="{user.website}">{user.website}</a>'
        assertInHTML(html, response.content.decode("utf-8"))


class TestSearchResults:
    def test_template_name_correct(self, auto_login_user):
        client, user = auto_login_user()
        response = client.get(SEARCH_URL)

        assertTemplateUsed(response, "pastes/search_results.html")

    def test_finds_appropriate_results(self, auto_login_user, create_paste):
        client, user = auto_login_user()
        # pastes that should be found
        create_paste(author=user, content="Search me dhfasjhdsafj search")
        create_paste(author=user, content="hfdjs dhfsaj search sdahfjjksd sdha")
        create_paste(author=user, title="Search me", content="dsfajfdhsafdjsah")
        # pastes that shouldn't be found
        create_paste(
            author=user,
            content="fasdfdsafdsafdsa",
        )
        create_paste(
            author=user,
            content="fdsadfsfsdafads",
        )

        response = client.get(SEARCH_URL, {"q": "search"})

        assert len(response.context["page_obj"]) == 3

    def test_query_in_context(self, auto_login_user):
        client, user = auto_login_user()

        response = client.get(SEARCH_URL, {"q": "search"})

        assert response.context["query"] == "search"


class TestUserFolderList:
    def test_template_name_correct(self, auto_login_user, create_folder):
        client, user = auto_login_user()
        folder = create_folder(created_by=user)

        response = client.get(
            reverse("pastes:user_folder", args=[user.username, folder.slug])
        )

        assertTemplateUsed(response, "pastes/user_list.html")

    def test_folder_and_user_in_context(self, auto_login_user, create_folder):
        client, user = auto_login_user()
        folder = create_folder(created_by=user)

        response = client.get(
            reverse("pastes:user_folder", args=[user.username, folder.slug])
        )

        assert folder == response.context["folder"]
        assert user == response.context["author"]

    def test_author_can_view_pastes_in_folder(
        self, auto_login_user, create_folder, create_paste
    ):
        client, user = auto_login_user()
        folder = create_folder(created_by=user)
        for _ in range(5):
            create_paste(author=user, folder=folder)

        response = client.get(
            reverse("pastes:user_folder", args=[user.username, folder.slug])
        )

        assert len(response.context["page_obj"]) == 5

    def test_user_cannot_view_folders_of_other_users(
        self, client, auto_login_user, create_folder, create_user
    ):
        client, user = auto_login_user()
        another_user = create_user()
        folder = create_folder(created_by=another_user)

        response = client.get(
            reverse("pastes:user_folder", args=[user.username, folder.slug])
        )

        assert response.status_code == 404

    def test_login_required(self, client, user, create_folder):
        folder = create_folder(created_by=user)

        response = client.get(
            reverse("pastes:user_folder", args=[user.username, folder.slug])
        )

        assertRedirects(
            response,
            login_redirect_url(
                reverse("pastes:user_folder", args=[user.username, folder.slug])
            ),
        )


class TestUserFolderUpdate:
    def test_template_name_correct(self, auto_login_user, create_folder):
        client, user = auto_login_user()
        folder = create_folder(created_by=user)

        response = client.get(
            reverse("pastes:user_folder_edit", args=[user.username, folder.slug])
        )

        assertTemplateUsed(response, "pastes/folder_form.html")

    def test_form_in_context(self, auto_login_user, create_folder):
        client, user = auto_login_user()
        folder = create_folder(created_by=user)

        response = client.get(
            reverse("pastes:user_folder_edit", args=[user.username, folder.slug])
        )
        form = response.context["form"]

        assert isinstance(form, forms.FolderForm)

    def test_success_url(self, auto_login_user, create_folder):
        client, user = auto_login_user()
        folder = create_folder(created_by=user)
        data = {
            "name": "Updated",
        }

        response = client.post(
            reverse("pastes:user_folder_edit", args=[user.username, folder.slug]),
            data=data,
        )
        folder.refresh_from_db()

        assertRedirects(
            response,
            folder.get_absolute_url(),
        )

    def test_folder_author_can_update_its_name(self, auto_login_user, create_folder):
        client, user = auto_login_user()
        folder = create_folder(created_by=user)
        data = {
            "name": "Updated",
        }

        client.post(
            reverse("pastes:user_folder_edit", args=[user.username, folder.slug]),
            data=data,
        )
        folder.refresh_from_db()

        assert folder.name == "Updated"

    def test_user_cannot_update_another_users_folder(
        self, create_folder, client, create_user, auto_login_user
    ):
        data = {
            "name": "Updated",
        }
        client, user = auto_login_user()
        another_user = create_user()
        folder = create_folder(created_by=another_user)

        response = client.post(
            reverse("pastes:user_folder_edit", args=[user.username, folder.slug]),
            data=data,
        )
        folder.refresh_from_db()

        assert folder.name == "Testing folder"
        assert response.status_code == 404


class TestUserFolderDelete:
    def test_template_name_correct(self, auto_login_user, create_folder):
        client, user = auto_login_user()
        folder = create_folder(created_by=user)

        response = client.get(
            reverse("pastes:user_folder_delete", args=[user.username, folder.slug])
        )

        assertTemplateUsed(response, "pastes/folder_delete.html")

    def test_success_url(self, auto_login_user, create_folder):
        client, user = auto_login_user()
        folder = create_folder(created_by=user)

        response = client.post(
            reverse("pastes:user_folder_delete", args=[user.username, folder.slug])
        )

        assertRedirects(
            response,
            reverse("pastes:user_pastes", args=[user.username]),
        )

    def test_folder_author_can_delete_folder(self, auto_login_user, create_folder):
        client, user = auto_login_user()
        folder = create_folder(created_by=user)

        client.post(
            reverse("pastes:user_folder_delete", args=[user.username, folder.slug])
        )

        assert Folder.objects.filter(created_by=user).count() == 0

    def test_user_cannot_delete_another_users_folder(
        self, auto_login_user, create_folder, create_user
    ):
        client, user = auto_login_user()
        another_user = create_user()
        folder = create_folder(created_by=another_user)

        response = client.post(
            reverse("pastes:user_folder_delete", args=[user.username, folder.slug])
        )

        assert folder.name == "Testing folder"
        assert response.status_code == 404


class TestPasteArchiveList:
    def test_template_name_correct(self, client):
        response = client.get(PASTES_ARCHIVE_URL)

        assertTemplateUsed(response, "pastes/archive.html")

    @override_settings(PASTES_ARCHIVE_LENGTH=2)
    def test_can_view_archive(self, client, create_paste):
        first_added_paste = create_paste()
        second_added_paste = create_paste()
        last_added_paste = create_paste()

        response = client.get(PASTES_ARCHIVE_URL)

        assert first_added_paste not in response.context["pastes"]
        assert second_added_paste in response.context["pastes"]
        assert last_added_paste in response.context["pastes"]

    def test_can_view_archive_of_specific_language(self, client, create_paste):
        first_added_paste = create_paste(syntax="python")
        second_added_paste = create_paste()
        last_added_paste = create_paste(syntax="python")

        response = client.get(reverse("pastes:syntax_archive", args=["python"]))

        assert first_added_paste in response.context["pastes"]
        assert second_added_paste not in response.context["pastes"]
        assert last_added_paste in response.context["pastes"]

    def test_syntax_in_context_of_language_archive(self, client):
        response = client.get(reverse("pastes:syntax_archive", args=["python"]))

        assert "Python" == response.context["syntax"]

    def test_displays_message_when_no_pastes(self, client):
        Paste.objects.all().delete()

        response = client.get(PASTES_ARCHIVE_URL)

        assertInHTML(
            "<p>There are no pastes yet.</p>", response.content.decode("utf-8")
        )


class TestEmbedPaste:
    def test_template_name_correct(self, client, create_paste):
        paste = create_paste()
        embed_url = reverse("pastes:embed", args=[paste.uuid])

        response = client.get(embed_url)

        assertTemplateUsed(response, "pastes/embed.html")

    def test_direct_link_to_image_in_context(self, client, create_paste):
        paste = create_paste()
        embed_url = reverse("pastes:embed", args=[paste.uuid])

        response = client.get(embed_url)

        assert (
            f"http://testserver/media/embed/{paste.uuid}.png"
            == response.context["direct_embed_link"]
        )

    def test_embed_image_is_displayed(self, client, create_paste):
        paste = create_paste()
        embed_url = reverse("pastes:embed", args=[paste.uuid])

        response = client.get(embed_url)

        html = f'<img src="{paste.embeddable_image.url}" alt="Paste\'s content represented as an image">'
        assertInHTML(html, response.content.decode("utf-8"))

    def test_cannot_embed_burnable_paste(self, client, create_paste):
        burnable_paste = create_paste(burn_after_read=True)
        embed_url = reverse("pastes:embed", args=[burnable_paste.uuid])

        response = client.get(embed_url)

        assert response.status_code == 404

    def test_cannot_embed_password_protected_paste(self, create_paste, client):
        paste_with_pass = create_paste(password="pass123")
        embed_url = reverse("pastes:embed", args=[paste_with_pass.uuid])

        response = client.get(embed_url)

        assert response.status_code == 404

    def test_cannot_embed_private_paste(self, create_paste, client):
        private_paste = create_paste(exposure=Paste.Exposure.PRIVATE)
        embed_url = reverse("pastes:embed", args=[private_paste.uuid])

        response = client.get(embed_url)

        assert response.status_code == 404

    def test_author_cannot_embed_their_private_paste(
        self, auto_login_user, create_paste
    ):
        client, user = auto_login_user()
        private_paste = create_paste(exposure=Paste.Exposure.PRIVATE, author=user)
        embed_url = reverse("pastes:embed", args=[private_paste.uuid])

        response = client.get(embed_url)

        assert response.status_code == 404


class TestPrintPaste:
    def test_template_name_correct(self, client, create_paste):
        paste = create_paste()
        print_url = reverse("pastes:print", args=[paste.uuid])

        response = client.get(print_url)

        assertTemplateUsed(response, "pastes/print.html")

    def test_print_window_is_loaded(self, client, create_paste):
        paste = create_paste()
        print_url = reverse("pastes:print", args=[paste.uuid])

        response = client.get(print_url)

        html = '<body onload="window.print()">'
        assert html in response.content.decode("utf-8")

    def test_displays_content_html(self, client, create_paste):
        paste = create_paste()
        print_url = reverse("pastes:print", args=[paste.uuid])

        response = client.get(print_url)

        assert paste.content_html in response.content.decode("utf-8")

    def test_cannot_print_burnable_paste(self, create_paste, client):
        burnable_paste = create_paste(burn_after_read=True)
        print_url = reverse("pastes:print", args=[burnable_paste.uuid])

        response = client.get(print_url)

        assert response.status_code == 404

    def test_cannot_print_password_protected_paste(self, create_paste, client):
        paste_with_pass = create_paste(password="pass123")
        print_url = reverse("pastes:print", args=[paste_with_pass.uuid])

        response = client.get(print_url)

        assert response.status_code == 404

    def test_cannot_print_private_paste(self, client, create_paste):
        private_paste = create_paste(exposure=Paste.Exposure.PRIVATE)
        print_url = reverse("pastes:print", args=[private_paste.uuid])

        response = client.get(print_url)

        assert response.status_code == 404

    def test_can_print_private_paste_if_its_author(self, create_paste, auto_login_user):
        client, user = auto_login_user()
        paste = create_paste(author=user)
        print_url = reverse("pastes:print", args=[paste.uuid])

        response = client.get(print_url)

        assert response.status_code == 200


class TestReportPaste:
    def template_name_correct(self, client, create_paste):
        paste = create_paste()
        report_url = reverse("pastes:report", args=[paste.uuid])

        response = client.get(report_url)

        assertTemplateUsed(response, "pastes/report.html")

    def test_form_class_correct(self, client, create_paste):
        paste = create_paste()
        report_url = reverse("pastes:report", args=[paste.uuid])

        response = client.get(report_url)

        assert isinstance(response.context["form"], forms.ReportForm)

    def test_reported_paste_in_context(self, client, create_paste):
        paste = create_paste()
        report_url = reverse("pastes:report", args=[paste.uuid])

        response = client.get(report_url)

        assert response.context["reported_paste"] == paste

    def test_can_report_paste(self, client, create_paste):
        paste = create_paste()
        report_url = reverse("pastes:report", args=[paste.uuid])
        data = {"reason": "Testing", "reporter_name": "Tester"}

        client.post(report_url, data=data)

        created_report = Report.objects.first()
        assert Report.objects.count() == 1
        assert created_report.paste == paste

    def test_redirects_to_paste_on_success(self, client, create_paste):
        paste = create_paste()
        report_url = reverse("pastes:report", args=[paste.uuid])
        data = {"reason": "Testing", "reporter_name": "Tester"}

        response = client.post(report_url, data=data)

        assertRedirects(response, paste.get_absolute_url())

    def test_cannot_report_burnable_paste(self, client, create_paste):
        burnable_paste = create_paste(burn_after_read=True)
        report_url = reverse("pastes:report", args=[burnable_paste.uuid])

        response = client.get(report_url)

        assert response.status_code == 404

    def test_cannot_report_password_protected_paste(self, client, create_paste):
        paste_with_pass = create_paste(password="pass123")
        report_url = reverse("pastes:report", args=[paste_with_pass.uuid])

        response = client.get(report_url)

        assert response.status_code == 404

    def test_cannot_report_private_paste(self, client, create_paste):
        private_paste = create_paste(exposure=Paste.Exposure.PRIVATE)
        report_url = reverse("pastes:report", args=[private_paste.uuid])

        response = client.get(report_url)

        assert response.status_code == 404

    def test_cannot_report_users_own_pastes(self, auto_login_user, create_paste):
        client, user = auto_login_user()
        paste = create_paste(author=user)
        report_url = reverse("pastes:report", args=[paste.uuid])

        response = client.get(report_url)

        assert response.status_code == 404


class TestSyntaxLanguages:
    def test_template_name_correct(self, client):
        response = client.get(LANGUAGES_URL)

        assertTemplateUsed(response, "pastes/syntax_languages.html")

    def test_displays_language_list_with_count(self, client, create_paste):
        for _ in range(3):
            create_paste(content="hi", syntax="python")
        for _ in range(2):
            create_paste(content="hi", syntax="javascript")

        response = client.get(LANGUAGES_URL)

        assert response.context["languages"][0]["syntax"] == "javascript"
        assert response.context["languages"][0]["used"] == 2
        assert response.context["languages"][1]["syntax"] == "python"
        assert response.context["languages"][1]["used"] == 3


class TestBackupUserPastes:
    def test_login_required(self, client):
        response = client.get(BACKUP_URL)

        assertRedirects(response, login_redirect_url(BACKUP_URL))

    @patch.object(
        timezone,
        "now",
        return_value=datetime.datetime(
            2022, 6, 24, 12, 00, tzinfo=datetime.timezone.utc
        ),
    )
    def test_backup_archive_with_correct_name(
        self, mock, auto_login_user, create_paste
    ):
        client, user = auto_login_user()
        create_paste(content="Hi", author=user)

        response = client.post(BACKUP_URL)

        assert (
            response.headers["Content-Disposition"]
            == "attachment; filename=pastemate_backup_20220624.zip"
        )
