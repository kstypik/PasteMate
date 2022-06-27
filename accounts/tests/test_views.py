import tempfile
from io import BytesIO

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from pastemate_project.utils import login_redirect_url
from PIL import Image

from ..forms import AccountDeleteForm, AvatarForm, PreferencesForm, ProfileForm

User = get_user_model()

ACCOUNT_DELETE_URL = reverse("accounts:delete")
AVATAR_URL = reverse("accounts:avatar")
PROFILE_UPDATE_URL = reverse("accounts:profile_update")
PREFERENCES_UPDATE_URL = reverse("accounts:preferences")


def create_image(width, height):
    image = Image.new("RGBA", (width, height))
    stream = BytesIO()
    image.save(stream, "PNG")
    stream.seek(0)
    return SimpleUploadedFile("avatar_for_testing.png", stream.read(), "image/jpeg")


class ProfileUpdateViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="Test", email="test@test.com")
        self.client.force_login(self.user)

    def test_login_required(self):
        response = Client().get(PROFILE_UPDATE_URL)

        self.assertRedirects(response, login_redirect_url(PROFILE_UPDATE_URL))

    def test_template_name_correct(self):
        response = self.client.get(PROFILE_UPDATE_URL)

        self.assertTemplateUsed(response, "account/profile_edit.html")

    def test_success_url_correct(self):
        response = self.client.post(
            PROFILE_UPDATE_URL,
            data={
                "location": "Testland",
                "website": "example.com",
            },
        )

        self.assertRedirects(response, PROFILE_UPDATE_URL)

    def test_form_class_correct(self):
        response = self.client.get(PROFILE_UPDATE_URL)

        self.assertIsInstance(response.context["form"], ProfileForm)

    def test_can_update_profile(self):
        data = {
            "location": "My updated location",
            "website": "https://newwebsite.com",
        }
        self.client.post(PROFILE_UPDATE_URL, data=data)
        self.user.refresh_from_db()

        self.assertEqual(self.user.location, "My updated location")
        self.assertEqual(self.user.website, "https://newwebsite.com")


class AvatarUpdateViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="Test", email="test@test.com")
        self.client.force_login(self.user)

        self.avatar = create_image(100, 100)

    def test_login_required(self):
        response = Client().get(AVATAR_URL)

        self.assertRedirects(response, login_redirect_url(AVATAR_URL))

    def test_template_name_correct(self):
        response = self.client.get(AVATAR_URL)

        self.assertTemplateUsed(response, "account/avatar_edit.html")

    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def test_success_url_correct(self):
        response = self.client.post(
            AVATAR_URL,
            data={"avatar": self.avatar},
        )

        self.assertRedirects(response, PROFILE_UPDATE_URL)

    def test_form_class_correct(self):
        response = self.client.get(AVATAR_URL)

        self.assertIsInstance(response.context["form"], AvatarForm)

    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def test_can_update_profile(self):
        self.client.post(
            AVATAR_URL,
            data={"avatar": self.avatar},
        )
        self.user.refresh_from_db()

        avatar_without_ext = self.avatar.name.split(".")[0]
        self.assertIn(avatar_without_ext, self.user.avatar.name)


class AccountDeleteViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="Test", email="test@test.com", password="test123"
        )
        self.client.force_login(self.user)

    def test_login_required(self):
        response = Client().get(ACCOUNT_DELETE_URL)

        self.assertRedirects(response, login_redirect_url(ACCOUNT_DELETE_URL))

    def test_template_name_correct(self):
        response = self.client.get(ACCOUNT_DELETE_URL)

        self.assertTemplateUsed(response, "account/account_delete.html")

    def test_form_class_correct(self):
        response = self.client.get(ACCOUNT_DELETE_URL)

        self.assertIsInstance(response.context["form"], AccountDeleteForm)

    def test_success_url(self):
        response = self.client.post(ACCOUNT_DELETE_URL, data={"password": "test123"})

        self.assertRedirects(response, reverse("pastes:create"))

    def test_can_delete_account(self):
        self.client.post(ACCOUNT_DELETE_URL, data={"password": "test123"})

        self.assertEqual(User.objects.count(), 0)


class PreferencesUpdateViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="Test",
            email="test@test.com",
        )
        self.client.force_login(self.user)

    def test_login_required(self):
        response = Client().get(PREFERENCES_UPDATE_URL)

        self.assertRedirects(response, login_redirect_url(PREFERENCES_UPDATE_URL))

    def test_template_name_correct(self):
        response = self.client.get(PREFERENCES_UPDATE_URL)

        self.assertTemplateUsed(response, "account/preferences.html")

    def test_form_class_correct(self):
        response = self.client.get(PREFERENCES_UPDATE_URL)

        self.assertIsInstance(response.context["form"], PreferencesForm)

    def test_success_url(self):
        data = {
            "default_syntax": "python",
            "default_expiration_interval_symbol": "10M",
            "default_exposure": "PR",
        }
        response = self.client.post(PREFERENCES_UPDATE_URL, data=data)

        self.assertRedirects(response, PREFERENCES_UPDATE_URL)

    def test_can_update_preferences(self):
        data = {
            "default_syntax": "python",
            "default_expiration_interval_symbol": "10M",
            "default_exposure": "PR",
        }
        self.client.post(PREFERENCES_UPDATE_URL, data=data)
        self.user.refresh_from_db()

        self.assertEqual(self.user.preferences.default_syntax, "python")
        self.assertEqual(
            self.user.preferences.default_expiration_interval_symbol, "10M"
        )
        self.assertEqual(self.user.preferences.default_exposure, "PR")
