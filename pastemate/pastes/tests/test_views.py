import datetime
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.utils import formats, timezone

from config.utils import login_redirect_url

from .. import forms
from ..models import Folder, Paste, Report

User = get_user_model()

PASTE_CREATE_URL = reverse("pastes:create")
PASTES_ARCHIVE_URL = reverse("pastes:archive")
LANGUAGES_URL = reverse("pastes:syntax_languages")
BACKUP_URL = reverse("pastes:backup")


class PasteCreateViewTest(TestCase):
    def test_template_name_correct(self):
        response = self.client.get(PASTE_CREATE_URL)

        self.assertTemplateUsed(response, "pastes/form.html")

    def test_form_class_correct(self):
        response = self.client.get(PASTE_CREATE_URL)

        self.assertIsInstance(response.context["form"], forms.PasteForm)

    def test_action_type_in_template(self):
        action_type = "Create New Paste"

        response = self.client.get(PASTE_CREATE_URL)

        self.assertContains(response, action_type)

    @patch("hcaptcha_field.fields.hCaptchaField.validate", return_value=True)
    def test_success_url(self, mock):
        data = {
            "content": "Hello World!",
            "syntax": "text",
            "exposure": "PU",
            "h-captcha-response": "valid",
        }
        response = self.client.post(PASTE_CREATE_URL, data=data)
        paste = Paste.objects.first()

        self.assertRedirects(response, paste.get_absolute_url())

    @patch("hcaptcha_field.fields.hCaptchaField.validate", return_value=True)
    def test_guest_can_create_paste(self, mock):
        data = {
            "content": "Hello World!",
            "syntax": "text",
            "exposure": "PU",
            "h-captcha-response": "valid",
        }
        self.client.post(PASTE_CREATE_URL, data=data)
        paste = Paste.objects.first()

        self.assertEqual(Paste.objects.count(), 1)
        self.assertEqual(paste.content, "Hello World!")
        self.assertEqual(paste.author, None)

    def test_user_can_create_paste(self):
        user = User.objects.create_user(username="Tester", email="test@test.com")
        self.client.force_login(user)

        data = {
            "content": "Hello World!",
            "syntax": "text",
            "exposure": "PU",
        }
        self.client.post(PASTE_CREATE_URL, data=data)
        paste = Paste.objects.first()

        self.assertEqual(Paste.objects.count(), 1)
        self.assertEqual(paste.content, "Hello World!")
        self.assertEqual(paste.author, user)


class PasteCloneViewTest(TestCase):
    def setUp(self):
        self.cloned_paste = Paste.objects.create(content="Hello World!")
        self.user = User.objects.create_user(username="Tester", email="test@test.com")
        self.client.force_login(self.user)

        self.paste_clone_url = reverse("pastes:clone", args=[self.cloned_paste.uuid])

    def test_action_type_in_template(self):
        action_type = "Clone Paste"

        response = self.client.get(self.paste_clone_url)

        self.assertContains(response, action_type)

    def test_login_required(self):
        response = Client().get(self.paste_clone_url)

        self.assertRedirects(response, login_redirect_url(self.paste_clone_url))

    def test_correct_initial_data(self):
        response = self.client.get(self.paste_clone_url)
        form = response.context["form"]

        self.assertEqual(form.initial["content"], self.cloned_paste.content)
        self.assertEqual(form.initial["syntax"], self.cloned_paste.syntax)
        self.assertEqual(form.initial["title"], self.cloned_paste.title)

    def test_can_clone_paste_with_default_data(self):
        data = {
            "content": self.cloned_paste.content,
            "title": self.cloned_paste.title,
            "syntax": self.cloned_paste.syntax,
            "exposure": "PU",
        }
        self.client.post(self.paste_clone_url, data=data)
        paste = Paste.objects.first()

        self.assertEqual(Paste.objects.count(), 2)
        self.assertEqual(paste.content, self.cloned_paste.content)
        self.assertEqual(paste.syntax, self.cloned_paste.syntax)
        self.assertEqual(paste.title, self.cloned_paste.title)

    def test_can_clone_paste_with_custom_data(self):
        data = {
            "title": "My Cloned Paste",
            "syntax": "python",
            "content": "print('Hello World')",
            "exposure": "PU",
        }
        self.client.post(self.paste_clone_url, data=data)
        paste = Paste.objects.first()

        self.assertEqual(Paste.objects.count(), 2)
        self.assertEqual(paste.content, "print('Hello World')")
        self.assertEqual(paste.syntax, "python")
        self.assertEqual(paste.title, "My Cloned Paste")

    def test_cannot_clone_private_paste(self):
        private_paste_author = User.objects.create_user(
            username="Private Author", email="private@author.com"
        )
        private_paste = Paste.objects.create(
            content="Hello World!", exposure="PR", author=private_paste_author
        )

        response = self.client.get(reverse("pastes:clone", args=[private_paste.uuid]))

        self.assertEqual(response.status_code, 404)


class PasteDetailViewTest(TestCase):
    def setUp(self):
        self.logged_user = User.objects.create_user(
            username="Test",
            email="test@test.com",
        )
        self.paste_author = User.objects.create_user(
            username="Another Test",
            email="anothertest@test.com",
            location="Spain",
            website="http://example.com",
        )
        self.client.force_login(self.logged_user)
        self.paste = Paste.objects.create(
            content="Hello World",
            author=self.paste_author,
            expiration_symbol=Paste.TEN_MINUTES,
        )
        self.paste_url = self.paste.get_absolute_url()

    def test_template_name_correct(self):
        response = self.client.get(self.paste_url)

        self.assertTemplateUsed(response, "pastes/detail.html")

    def test_redirects_pastes_with_passwords_to_appropriate_view(self):
        paste_with_pass = Paste.objects.create(content="Hello", password="pass12")

        response = self.client.get(paste_with_pass.get_absolute_url())

        self.assertRedirects(
            response,
            reverse("pastes:detail_with_password", args=[paste_with_pass.uuid]),
        )

    def test_can_burn_paste(self):
        burnable_paste = Paste.objects.create(content="Hello", burn_after_read=True)
        burnable_paste_uuid = burnable_paste.uuid

        self.client.post(burnable_paste.get_absolute_url())

        self.assertFalse(Paste.objects.filter(uuid=burnable_paste_uuid).exists())

    def test_displays_private_message_to_author_url_for_logged(self):
        response = self.client.get(self.paste_url)

        pm_url = reverse(
            "pinax_messages:message_user_create", args=[self.paste_author.id]
        )
        self.assertContains(response, pm_url)

    def test_does_not_display_private_message_to_author_url_for_themselves(self):
        authors_paste = Paste.objects.create(content="hi", author=self.logged_user)
        response = self.client.get(authors_paste.get_absolute_url())

        pm_url = reverse(
            "pinax_messages:message_user_create", args=[self.logged_user.id]
        )
        self.assertNotContains(response, pm_url)

    def test_does_not_display_private_message_to_author_url_for_unlogged(self):
        response = Client().get(self.paste_url)

        pm_url = reverse(
            "pinax_messages:message_user_create", args=[self.paste_author.id]
        )
        self.assertNotContains(response, pm_url)

    def test_displays_correct_expiration_date_when_set(self):
        response = self.client.get(self.paste_url)

        expiration_date = formats.date_format(self.paste.expiration_date, "c")
        html = f'<span class="to-relative-datetime text-capitalize">{expiration_date}</span>'
        self.assertInHTML(html, response.content.decode("utf-8"))

    def test_displays_authors_location_when_set(self):
        response = self.client.get(self.paste_url)

        self.assertContains(response, self.paste_author.location)

    def test_displays_authors_website_when_set(self):
        response = self.client.get(self.paste_url)

        self.assertContains(response, self.paste_author.website)


class RawPasteDetailViewTest(TestCase):
    def setUp(self):
        self.paste = Paste.objects.create(content="print('Hello World')")

    def test_can_view_raw_paste_detail(self):
        response = self.client.get(reverse("pastes:raw_detail", args=[self.paste.uuid]))

        self.assertEqual(response.content.decode("utf-8"), self.paste.content)


class DownloadPasteViewTest(TestCase):
    def test_can_download_paste(self):
        paste = Paste.objects.create(content="Hello World", syntax="python")

        response = self.client.get(reverse("pastes:paste_download", args=[paste.uuid]))

        self.assertEqual(
            response.headers["Content-Disposition"],
            f'attachment; filename="paste-{paste.uuid}.txt"',
        )
        self.assertContains(response, paste.content)


class PasteDetailWithPasswordViewTest(TestCase):
    def setUp(self):
        self.paste = Paste.objects.create(
            content="Hello with password",
            password="pass123",
        )
        self.paste_url = reverse("pastes:detail_with_password", args=[self.paste.uuid])

    def test_template_name_correct(self):
        response = self.client.get(self.paste_url)

        self.assertTemplateUsed(response, "pastes/detail.html")

    def test_password_form_in_context(self):
        response = self.client.get(self.paste_url)
        form = response.context["password_form"]

        self.assertIsInstance(form, forms.PasswordProtectedPasteForm)

    def test_password_protected_in_context(self):
        response = self.client.get(self.paste_url)

        self.assertTrue(response.context["password_protected"])

    def test_redirects_to_normal_detail_on_GET_when_paste_has_no_password(self):
        paste_without_pass = Paste.objects.create(content="Hi")

        response = self.client.get(
            reverse("pastes:detail_with_password", args=[paste_without_pass.uuid])
        )

        self.assertRedirects(response, paste_without_pass.get_absolute_url())

    def test_redirects_to_normal_detail_on_POST_when_paste_has_no_password(self):
        paste_without_pass = Paste.objects.create(content="Hi")

        response = self.client.post(
            reverse("pastes:detail_with_password", args=[paste_without_pass.uuid])
        )

        self.assertRedirects(response, paste_without_pass.get_absolute_url())

    def test_can_access_paste_when_submitted_password_correct(self):
        response = self.client.post(
            self.paste_url,
            data={
                "password": "pass123",
            },
        )

        self.assertTrue(response.context["password_correct"])
        self.assertContains(response, self.paste.content)

    def test_cannot_access_paste_when_submitted_password_wrong(self):
        response = self.client.post(
            self.paste_url,
            data={
                "password": "incorrect",
            },
        )

        self.assertFalse(response.context.get("password_correct", False))
        self.assertNotContains(response, self.paste.content)

    def test_cannot_access_password_protected_paste_on_GET(self):
        response = self.client.get(
            self.paste_url,
        )

        self.assertNotContains(response, self.paste.content)

    def test_can_burn_paste_when_also_password_protected(self):
        burnable_paste_with_pass = Paste.objects.create(
            content="Hello", burn_after_read=True, password="pass123"
        )
        burnable_paste_uuid = burnable_paste_with_pass.uuid
        paste_url = reverse(
            "pastes:detail_with_password", args=[burnable_paste_with_pass.uuid]
        )

        self.client.post(paste_url, data={"password": "pass123"})

        self.assertFalse(Paste.objects.filter(uuid=burnable_paste_uuid).exists())

    def test_cannot_burn_paste_with_password_when_wrong_password_provided(self):
        burnable_paste_with_pass = Paste.objects.create(
            content="Hello", burn_after_read=True, password="pass123"
        )
        burnable_paste_uuid = burnable_paste_with_pass.uuid
        paste_url = reverse(
            "pastes:detail_with_password", args=[burnable_paste_with_pass.uuid]
        )

        self.client.post(paste_url, data={"password": "wrong"})

        self.assertTrue(Paste.objects.filter(uuid=burnable_paste_uuid).exists())

    def test_cannot_burn_paste_with_password_on_GET(self):
        burnable_paste_with_pass = Paste.objects.create(
            content="Hello", burn_after_read=True, password="pass123"
        )
        burnable_paste_uuid = burnable_paste_with_pass.uuid
        paste_url = reverse(
            "pastes:detail_with_password", args=[burnable_paste_with_pass.uuid]
        )

        self.client.get(paste_url)

        self.assertTrue(Paste.objects.filter(uuid=burnable_paste_uuid).exists())


class PasteUpdateViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="Tester", email="test@test.com")
        self.client.force_login(self.user)

        self.paste = Paste.objects.create(content="Hello", author=self.user)
        self.paste_url = reverse("pastes:update", args=[self.paste.uuid])

    def test_template_name_correct(self):
        response = self.client.get(self.paste_url)

        self.assertTemplateUsed(response, "pastes/form.html")

    def test_form_in_context(self):
        response = self.client.get(self.paste_url)
        form = response.context["form"]

        self.assertIsInstance(form, forms.PasteForm)

    def test_cannot_update_if_not_paste_author(self):
        client = Client()
        another_user = User.objects.create_user(
            username="NotAuthor", email="test@test.test"
        )
        client.force_login(another_user)

        response = client.get(self.paste_url)

        self.assertEqual(response.status_code, 404)

    def test_action_type_in_template(self):
        action_type = "Edit"

        response = self.client.get(self.paste_url)

        self.assertContains(response, action_type)

    def test_can_update_paste(self):
        data = {
            "content": "Hello Updated",
            "syntax": "html",
            "exposure": "PU",
        }

        self.client.post(self.paste_url, data=data)
        self.paste.refresh_from_db()

        self.assertEqual(self.paste.content, "Hello Updated")
        self.assertEqual(self.paste.syntax, "html")

    def test_redirects_to_paste_after_successful_update(self):
        data = {
            "content": "Hello Updated",
            "syntax": "html",
            "exposure": "PU",
        }

        response = self.client.post(self.paste_url, data=data)

        self.assertRedirects(response, self.paste.get_absolute_url())


class PasteDeleteViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="Tester", email="test@test.com")
        self.client.force_login(self.user)

        self.paste = Paste.objects.create(content="Hello", author=self.user)
        self.paste_url = reverse("pastes:delete", args=[self.paste.uuid])

    def test_template_name_correct(self):
        response = self.client.get(self.paste_url)

        self.assertTemplateUsed(response, "pastes/delete.html")

    def test_cannot_delete_if_not_paste_author(self):
        client = Client()
        another_user = User.objects.create_user(
            username="NotAuthor", email="test@test.test"
        )
        client.force_login(another_user)

        response = client.get(self.paste_url)

        self.assertEqual(response.status_code, 404)

    def test_can_delete_paste(self):
        self.client.post(self.paste_url)

        self.assertEqual(Paste.objects.count(), 0)

    def test_redirects_to_homepage_after_successful_delete(self):
        response = self.client.post(self.paste_url)

        self.assertRedirects(response, "/")


class UserPasteListViewTest(TestCase):
    def setUp(self):
        self.first_user = User.objects.create_user(
            username="logged",
            email="logged@email.com",
            location="Japan",
            website="http://hkjlgs.com",
        )
        self.client.force_login(self.first_user)

        self.another_user = User.objects.create_user(
            username="another_user", email="another@user.com"
        )
        self.another_client = Client()
        self.another_client.force_login(self.another_user)

        self.first_user_userlist = reverse(
            "pastes:user_pastes", args=[self.first_user.username]
        )
        self.another_user_userlist = reverse(
            "pastes:user_pastes", args=[self.another_user.username]
        )

        self.public_paste = Paste.objects.create(
            content="Public",
            exposure="PU",
            author=self.first_user,
        )
        self.unlisted_paste = Paste.objects.create(
            content="Unlisted", exposure="UN", author=self.first_user
        )
        self.private_paste = Paste.objects.create(
            content="Priv", exposure="PR", author=self.first_user
        )
        self.expiring_paste = Paste.objects.create(
            content="Expires",
            author=self.first_user,
            expiration_symbol=Paste.TEN_MINUTES,
        )

        self.folder1 = Folder.objects.create(name="folder1", created_by=self.first_user)
        self.folder2 = Folder.objects.create(name="folder2", created_by=self.first_user)

    def test_template_name_correct(self):
        response = self.client.get(self.first_user_userlist)

        self.assertTemplateUsed(response, "pastes/user_list.html")

    def test_user_can_see_their_own_pastes(self):
        response = self.client.get(self.first_user_userlist)

        self.assertIn(self.public_paste, response.context["page_obj"])
        self.assertIn(self.unlisted_paste, response.context["page_obj"])
        self.assertIn(self.private_paste, response.context["page_obj"])

    def test_others_cannot_see_users_private_pastes(self):
        response = self.another_client.get(self.first_user_userlist)

        self.assertIn(self.public_paste, response.context["page_obj"])
        self.assertNotIn(self.unlisted_paste, response.context["page_obj"])
        self.assertNotIn(self.private_paste, response.context["page_obj"])

    def test_user_can_see_their_list_as_guest(self):
        response = self.client.get(self.first_user_userlist, {"guest": "1"})

        self.assertIn(self.public_paste, response.context["page_obj"])
        self.assertNotIn(self.unlisted_paste, response.context["page_obj"])
        self.assertNotIn(self.private_paste, response.context["page_obj"])

    def test_user_can_see_their_folders_on_list(self):
        response = self.client.get(self.first_user_userlist)

        self.assertIn(self.folder1, response.context["folders"])
        self.assertIn(self.folder2, response.context["folders"])

    def test_show_count_of_pastes_in_folder(self):
        Paste.objects.create(content="hi", folder=self.folder1)
        Paste.objects.create(content="hi", folder=self.folder1)
        Paste.objects.create(content="hi", folder=self.folder2)
        Folder.objects.create(name="folder3", created_by=self.first_user)

        response = self.client.get(self.first_user_userlist)

        self.assertEqual(response.context["folders"].get(name="folder1").num_pastes, 2)
        self.assertEqual(response.context["folders"].get(name="folder2").num_pastes, 1)
        self.assertEqual(response.context["folders"].get(name="folder3").num_pastes, 0)

    def test_user_cannot_see_other_users_folders_on_list(self):
        response = self.another_client.get(self.another_user_userlist)

        self.assertNotIn(self.folder1, response.context["folders"])
        self.assertNotIn(self.folder2, response.context["folders"])

    @override_settings(PASTES_USER_LIST_PAGINATE_BY=2)
    def test_user_list_is_paginated(self):
        for _ in range(10):
            Paste.objects.create(content="paginate me", author=self.another_user)

        response = self.another_client.get(self.another_user_userlist)

        self.assertEqual(response.context["page_obj"].paginator.num_pages, 5)

    def test_show_statistics(self):
        for _ in range(2):
            Paste.objects.create(content="test", author=self.first_user, exposure="PU")

        for _ in range(3):
            Paste.objects.create(content="test", author=self.first_user, exposure="PR")

        for _ in range(4):
            Paste.objects.create(content="test", author=self.first_user, exposure="UN")

        response = self.client.get(self.first_user_userlist)

        stats = response.context["stats"]
        self.assertEqual(stats["total_pastes"], 13)
        self.assertEqual(stats["public_pastes"], 4)
        self.assertEqual(stats["unlisted_pastes"], 5)
        self.assertEqual(stats["private_pastes"], 4)

    def test_displays_correct_expiration_date_when_set(self):
        response = self.client.get(self.first_user_userlist)

        expiration_date = formats.date_format(self.expiring_paste.expiration_date, "c")
        html = f'<span class="to-relative-datetime">{expiration_date}</span>'
        self.assertInHTML(html, response.content.decode("utf-8"))

    def test_displays_authors_location_when_set(self):
        response = self.client.get(self.first_user_userlist)

        self.assertContains(response, self.first_user.location)

    def test_displays_authors_website_when_set(self):
        response = self.client.get(self.first_user_userlist)

        html = f'<a href="{self.first_user.website}">{self.first_user.website}</a>'
        self.assertInHTML(html, response.content.decode("utf-8"))


class SearchResultsViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="logged", email="logged@email.com"
        )
        self.client.force_login(self.user)

        # pastes that should be found
        Paste.objects.create(
            author=self.user,
            content="Search me dhfasjhdsafj search",
        )
        Paste.objects.create(
            author=self.user,
            content="hfdjs dhfsaj search sdahfjjksd sdha",
        )
        Paste.objects.create(
            author=self.user, content="dsfajfdhsafdjsah", title="Search me"
        )

        # pastes that shouldn't be found
        Paste.objects.create(
            author=self.user,
            content="fasdfdsafdsafdsa",
        )
        Paste.objects.create(
            author=self.user,
            content="fdsadfsfsdafads",
        )

        self.search_url = reverse("pastes:search")

    def test_template_name_correct(self):
        response = self.client.get(self.search_url)

        self.assertTemplateUsed(response, "pastes/search_results.html")

    def test_finds_appropriate_results(self):
        response = self.client.get(self.search_url, {"q": "search"})

        self.assertEqual(len(response.context["page_obj"]), 3)

    def test_query_in_context(self):
        response = self.client.get(self.search_url, {"q": "search"})

        self.assertEqual(response.context["query"], "search")


class UserFolderListViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="test", email="test@test.com")
        self.client.force_login(self.user)

        self.folder = Folder.objects.create(name="Testing folder", created_by=self.user)

        self.folder_list_url = reverse(
            "pastes:user_folder", args=[self.user.username, self.folder.slug]
        )
        for _ in range(5):
            Paste.objects.create(content="Hi", folder=self.folder, author=self.user)

    def test_template_name_correct(self):
        response = self.client.get(self.folder_list_url)

        self.assertTemplateUsed(response, "pastes/user_list.html")

    def test_folder_and_user_in_context(self):
        response = self.client.get(self.folder_list_url)

        self.assertEqual(self.folder, response.context["folder"])
        self.assertEqual(self.user, response.context["author"])

    def test_author_can_view_pastes_in_folder(self):
        response = self.client.get(self.folder_list_url)

        self.assertEqual(len(response.context["page_obj"]), 5)

    def test_user_cannot_view_folders_of_other_users(self):
        another_user = User.objects.create_user(
            username="another", email="another@another.com"
        )
        client = Client()
        client.force_login(another_user)
        response = client.get(self.folder_list_url)

        self.assertEqual(response.status_code, 404)

    def test_login_required(self):
        response = Client().get(self.folder_list_url)

        self.assertRedirects(response, login_redirect_url(self.folder_list_url))


class UserFolderUpdateViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="test", email="test@test.com")
        self.client.force_login(self.user)

        self.folder = Folder.objects.create(name="Testing folder", created_by=self.user)

        self.folder_edit_url = reverse(
            "pastes:user_folder_edit", args=[self.user.username, self.folder.slug]
        )

    def test_template_name_correct(self):
        response = self.client.get(self.folder_edit_url)

        self.assertTemplateUsed(response, "pastes/folder_form.html")

    def test_form_in_context(self):
        response = self.client.get(self.folder_edit_url)
        form = response.context["form"]

        self.assertIsInstance(form, forms.FolderForm)

    def test_success_url(self):
        data = {
            "name": "Updated",
        }
        response = self.client.post(self.folder_edit_url, data=data)
        self.folder.refresh_from_db()

        self.assertRedirects(
            response,
            reverse("pastes:user_folder", args=[self.user.username, self.folder.slug]),
        )

    def test_folder_author_can_update_its_name(self):
        data = {
            "name": "Updated",
        }
        self.client.post(self.folder_edit_url, data=data)
        self.folder.refresh_from_db()

        self.assertEqual(self.folder.name, "Updated")

    def test_user_cannot_update_another_users_folder(self):
        data = {
            "name": "Updated",
        }
        another_client = Client()
        another_user = User.objects.create_user(
            username="another", email="another@user.com"
        )
        another_client.force_login(another_user)

        response = another_client.post(self.folder_edit_url, data=data)
        self.folder.refresh_from_db()

        self.assertEqual(self.folder.name, "Testing folder")
        self.assertEqual(response.status_code, 404)


class UserFolderDeleteViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="test", email="test@test.com")
        self.client.force_login(self.user)

        self.folder = Folder.objects.create(name="Testing folder", created_by=self.user)

        self.folder_delete_url = reverse(
            "pastes:user_folder_delete", args=[self.user.username, self.folder.slug]
        )

    def test_template_name_correct(self):
        response = self.client.get(self.folder_delete_url)

        self.assertTemplateUsed(response, "pastes/folder_delete.html")

    def test_success_url(self):
        response = self.client.post(self.folder_delete_url)

        self.assertRedirects(
            response,
            reverse("pastes:user_pastes", args=[self.user.username]),
        )

    def test_folder_author_can_delete_folder(self):
        self.client.post(self.folder_delete_url)

        self.assertEqual(Folder.objects.filter(created_by=self.user).count(), 0)

    def test_user_cannot_delete_another_users_folder(self):
        another_client = Client()
        another_user = User.objects.create_user(
            username="another", email="another@user.com"
        )
        another_client.force_login(another_user)

        response = another_client.post(self.folder_delete_url)

        self.assertEqual(self.folder.name, "Testing folder")
        self.assertEqual(response.status_code, 404)


class PasteArchiveListViewTest(TestCase):
    def setUp(self):
        self.first_added_paste = Paste.objects.create(content="no1", syntax="python")
        self.second_added_paste = Paste.objects.create(content="no2")
        self.last_added_paste = Paste.objects.create(content="no3", syntax="python")

    def test_template_name_correct(self):
        response = self.client.get(PASTES_ARCHIVE_URL)

        self.assertTemplateUsed(response, "pastes/archive.html")

    @override_settings(PASTES_ARCHIVE_LENGTH=2)
    def test_can_view_archive(self):
        response = self.client.get(PASTES_ARCHIVE_URL)

        self.assertNotIn(self.first_added_paste, response.context["pastes"])
        self.assertIn(self.second_added_paste, response.context["pastes"])
        self.assertIn(self.last_added_paste, response.context["pastes"])

    def test_can_view_archive_of_specific_language(self):
        response = self.client.get(reverse("pastes:syntax_archive", args=["python"]))

        self.assertIn(self.first_added_paste, response.context["pastes"])
        self.assertNotIn(self.second_added_paste, response.context["pastes"])
        self.assertIn(self.last_added_paste, response.context["pastes"])

    def test_syntax_in_context_of_language_archive(self):
        response = self.client.get(reverse("pastes:syntax_archive", args=["python"]))

        self.assertEqual("Python", response.context["syntax"])

    def test_displays_message_when_no_pastes(self):
        Paste.objects.all().delete()

        response = self.client.get(PASTES_ARCHIVE_URL)

        self.assertInHTML(
            "<p>There are no pastes yet.</p>", response.content.decode("utf-8")
        )


class EmbedPasteViewTest(TestCase):
    def setUp(self):
        self.paste = Paste.objects.create(content="Hello World")
        self.embed_url = reverse("pastes:embed", args=[self.paste.uuid])

    def test_template_name_correct(self):
        response = self.client.get(self.embed_url)

        self.assertTemplateUsed(response, "pastes/embed.html")

    def test_direct_link_to_image_in_context(self):
        response = self.client.get(self.embed_url)

        self.assertEqual(
            f"http://testserver/media/embed/{self.paste.uuid}.png",
            response.context["direct_embed_link"],
        )

    def test_embed_image_is_displayed(self):
        response = self.client.get(self.embed_url)

        html = f'<img src="{self.paste.embeddable_image.url}" alt="Paste\'s content represented as an image">'
        self.assertInHTML(html, response.content.decode("utf-8"))

    def test_cannot_embed_burnable_paste(self):
        burnable_paste = Paste.objects.create(content="Hi", burn_after_read=True)

        response = self.client.get(reverse("pastes:embed", args=[burnable_paste.uuid]))

        self.assertEqual(response.status_code, 404)

    def test_cannot_embed_password_protected_paste(self):
        paste_with_pass = Paste.objects.create(content="Hi", password="pass123")

        response = self.client.get(reverse("pastes:embed", args=[paste_with_pass.uuid]))

        self.assertEqual(response.status_code, 404)

    def test_cannot_embed_private_paste(self):
        private_paste = Paste.objects.create(
            content="Hi", exposure=Paste.Exposure.PRIVATE
        )

        response = self.client.get(reverse("pastes:embed", args=[private_paste.uuid]))

        self.assertEqual(response.status_code, 404)

    def test_author_cannot_embed_their_private_paste(self):
        user = User.objects.create(username="TEST", email="test@ters.com")
        self.client.force_login(user)
        private_paste = Paste.objects.create(
            content="Hi", exposure=Paste.Exposure.PRIVATE, author=user
        )

        response = self.client.get(reverse("pastes:embed", args=[private_paste.uuid]))

        self.assertEqual(response.status_code, 404)


class PrintPasteViewTest(TestCase):
    def setUp(self):
        self.paste = Paste.objects.create(content="Hello World")
        self.print_url = reverse("pastes:print", args=[self.paste.uuid])

    def test_template_name_correct(self):
        response = self.client.get(self.print_url)

        self.assertTemplateUsed(response, "pastes/print.html")

    def test_print_window_is_loaded(self):
        response = self.client.get(self.print_url)

        html = '<body onload="window.print()">'
        self.assertIn(html, response.content.decode("utf-8"))

    def test_displays_content_html(self):
        response = self.client.get(self.print_url)

        self.assertIn(self.paste.content_html, response.content.decode("utf-8"))

    def test_cannot_print_burnable_paste(self):
        burnable_paste = Paste.objects.create(content="Hi", burn_after_read=True)

        response = self.client.get(reverse("pastes:print", args=[burnable_paste.uuid]))

        self.assertEqual(response.status_code, 404)

    def test_cannot_print_password_protected_paste(self):
        paste_with_pass = Paste.objects.create(content="Hi", password="pass123")

        response = self.client.get(reverse("pastes:print", args=[paste_with_pass.uuid]))

        self.assertEqual(response.status_code, 404)

    def test_cannot_print_private_paste(self):
        private_paste = Paste.objects.create(
            content="Hi", exposure=Paste.Exposure.PRIVATE
        )

        response = self.client.get(reverse("pastes:print", args=[private_paste.uuid]))

        self.assertEqual(response.status_code, 404)

    def test_can_print_private_paste_if_its_author(self):
        user = User.objects.create_user(username="User", email="user@user.com")
        self.client.force_login(user)
        private_paste_with_author = Paste.objects.create(
            content="Hi", exposure=Paste.Exposure.PRIVATE, author=user
        )

        response = self.client.get(
            reverse("pastes:print", args=[private_paste_with_author.uuid])
        )

        self.assertEqual(response.status_code, 200)


class ReportPasteViewTest(TestCase):
    def setUp(self):
        self.paste = Paste.objects.create(content="Hello")
        self.report_url = reverse("pastes:report", args=[self.paste.uuid])

    def template_name_correct(self):
        response = self.client.get(self.report_url)

        self.assertTemplateUsed(response, "pastes/report.html")

    def test_form_class_correct(self):
        response = self.client.get(self.report_url)

        self.assertIsInstance(response.context["form"], forms.ReportForm)

    def test_reported_paste_in_context(self):
        response = self.client.get(self.report_url)

        self.assertEqual(response.context["reported_paste"], self.paste)

    def test_can_report_paste(self):
        data = {"reason": "Testing", "reporter_name": "Tester"}

        self.client.post(self.report_url, data=data)

        created_report = Report.objects.first()
        self.assertEqual(Report.objects.count(), 1)
        self.assertEqual(created_report.paste, self.paste)

    def test_redirects_to_paste_on_success(self):
        data = {"reason": "Testing", "reporter_name": "Tester"}

        response = self.client.post(self.report_url, data=data)

        self.assertRedirects(response, self.paste.get_absolute_url())

    def test_cannot_report_burnable_paste(self):
        burnable_paste = Paste.objects.create(content="Hi", burn_after_read=True)

        response = self.client.get(reverse("pastes:report", args=[burnable_paste.uuid]))

        self.assertEqual(response.status_code, 404)

    def test_cannot_report_password_protected_paste(self):
        paste_with_pass = Paste.objects.create(content="Hi", password="pass123")

        response = self.client.get(
            reverse("pastes:report", args=[paste_with_pass.uuid])
        )

        self.assertEqual(response.status_code, 404)

    def test_cannot_report_private_paste(self):
        private_paste = Paste.objects.create(
            content="Hi", exposure=Paste.Exposure.PRIVATE
        )

        response = self.client.get(reverse("pastes:report", args=[private_paste.uuid]))

        self.assertEqual(response.status_code, 404)

    def test_cannot_report_users_own_pastes(self):
        user = User.objects.create_user(username="User", email="user@user.com")
        self.client.force_login(user)
        private_paste_with_author = Paste.objects.create(
            content="Hi", exposure=Paste.Exposure.PRIVATE, author=user
        )

        response = self.client.get(
            reverse("pastes:report", args=[private_paste_with_author.uuid])
        )

        self.assertEqual(response.status_code, 404)


class SyntaxLanguagesViewTest(TestCase):
    def test_template_name_correct(self):
        response = self.client.get(LANGUAGES_URL)

        self.assertTemplateUsed(response, "pastes/syntax_languages.html")

    def test_displays_language_list_with_count(self):
        for _ in range(3):
            Paste.objects.create(content="hi", syntax="python")
        for _ in range(2):
            Paste.objects.create(content="hi", syntax="javascript")

        response = self.client.get(LANGUAGES_URL)

        self.assertEqual(response.context["languages"][0]["syntax"], "javascript")
        self.assertEqual(response.context["languages"][0]["used"], 2)
        self.assertEqual(response.context["languages"][1]["syntax"], "python")
        self.assertEqual(response.context["languages"][1]["used"], 3)


class BackupUserPastesView(TestCase):
    def test_login_required(self):
        response = self.client.get(BACKUP_URL)

        self.assertRedirects(response, login_redirect_url(BACKUP_URL))

    @patch.object(
        timezone,
        "now",
        return_value=datetime.datetime(
            2022, 6, 24, 12, 00, tzinfo=datetime.timezone.utc
        ),
    )
    def test_backup_archive_with_correct_name(self, mock):
        user = User.objects.create_user(username="Test", email="test@test.com")
        self.client.force_login(user)
        Paste.objects.create(content="Hi", author=user)

        response = self.client.post(BACKUP_URL)

        self.assertEqual(
            response.headers["Content-Disposition"],
            "attachment; filename=pastemate_backup_20220624.zip",
        )
