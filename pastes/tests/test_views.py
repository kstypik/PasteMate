from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from pastemate_project.utils import login_redirect_url

from .. import forms
from ..models import Paste
from ..views import PasteDetailView

User = get_user_model()

PASTE_CREATE_URL = reverse("pastes:create")


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
            "h-captcha-response": "valid",
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

        response = self.client.get(private_paste.get_absolute_url())

        self.assertEqual(response.status_code, 404)


class PasteDetailViewTest(TestCase):
    def setUp(self):
        self.paste = Paste.objects.create(content="Hello World")
        self.paste_url = self.paste.get_absolute_url()

    def test_template_name_correct(self):
        response = self.client.get(self.paste_url)

        self.assertTemplateUsed(response, "pastes/detail.html")

    def test_counts_hits(self):
        """Ensure the view counts hits with django-hitcount"""
        self.assertTrue(PasteDetailView.count_hit)

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

        response = self.client.post(burnable_paste.get_absolute_url())

        self.assertFalse(Paste.objects.filter(uuid=burnable_paste_uuid).exists())

    def test_burn_after_read_in_GET_context(self):
        burnable_paste = Paste.objects.create(content="Hello", burn_after_read=True)

        response = self.client.get(burnable_paste.get_absolute_url())

        self.assertTrue(response.context["burn_after_read"])


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
            f'attachment; filename="paste-{paste.uuid}.py"',
        )
        self.assertContains(response, paste.content)
