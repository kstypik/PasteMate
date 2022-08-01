from io import BytesIO

import pytest
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from PIL import Image
from pytest_django.asserts import assertRedirects, assertTemplateUsed

from pastemate.accounts.forms import (
    AccountDeleteForm,
    AvatarForm,
    PreferencesForm,
    ProfileForm,
)
from pastemate.accounts.models import Preferences
from pastemate.core.utils import login_redirect_url

pytestmark = pytest.mark.django_db

User = get_user_model()

ACCOUNT_DELETE_URL = reverse("accounts:delete")
AVATAR_URL = reverse("accounts:avatar")
PROFILE_UPDATE_URL = reverse("accounts:profile_update")
PREFERENCES_UPDATE_URL = reverse("accounts:preferences")


@pytest.fixture
def image(width=100, height=100):
    image = Image.new("RGBA", (width, height))
    stream = BytesIO()
    image.save(stream, "PNG")
    stream.seek(0)
    return SimpleUploadedFile("avatar_for_testing.png", stream.read(), "image/jpeg")


class TestProfileEdit:
    def test_login_required(self, client):
        response = client.get(PROFILE_UPDATE_URL)

        assertRedirects(response, login_redirect_url(PROFILE_UPDATE_URL))

    def test_template_name_correct(self, auto_login_user):
        client, user = auto_login_user()
        response = client.get(PROFILE_UPDATE_URL)

        assertTemplateUsed(response, "account/profile_edit.html")

    def test_success_url_correct(self, auto_login_user):
        client, user = auto_login_user()
        response = client.post(
            PROFILE_UPDATE_URL,
            data={
                "location": "Testland",
                "website": "example.com",
            },
        )

        assertRedirects(response, PROFILE_UPDATE_URL)

    def test_form_class_correct(self, auto_login_user):
        client, user = auto_login_user()
        response = client.get(PROFILE_UPDATE_URL)

        assert isinstance(response.context["form"], ProfileForm)

    def test_can_update_profile(self, auto_login_user):
        client, user = auto_login_user()
        data = {
            "location": "My updated location",
            "website": "https://newwebsite.com",
        }
        client.post(PROFILE_UPDATE_URL, data=data)
        user.refresh_from_db()

        assert user.location == "My updated location"
        assert user.website == "https://newwebsite.com"


class TestAvatarEdit:
    def test_login_required(self, client):
        response = client.get(AVATAR_URL)

        assertRedirects(response, login_redirect_url(AVATAR_URL))

    def test_template_name_correct(self, auto_login_user):
        client, user = auto_login_user()
        response = client.get(AVATAR_URL)

        assertTemplateUsed(response, "account/avatar_edit.html")

    def test_success_url_correct(self, auto_login_user, image):
        client, user = auto_login_user()
        response = client.post(
            AVATAR_URL,
            data={"avatar": image},
        )

        assertRedirects(response, PROFILE_UPDATE_URL)

    def test_form_class_correct(self, auto_login_user):
        client, user = auto_login_user()
        response = client.get(AVATAR_URL)

        assert isinstance(response.context["form"], AvatarForm)

    def test_can_update_profile(self, auto_login_user, image):
        client, user = auto_login_user()
        client.post(
            AVATAR_URL,
            data={"avatar": image},
        )
        user.refresh_from_db()

        avatar_without_ext = image.name.split(".")[0]
        assert avatar_without_ext in user.avatar.name


class TestAccountDelete:
    def test_login_required(self, client):
        response = client.get(ACCOUNT_DELETE_URL)

        assertRedirects(response, login_redirect_url(ACCOUNT_DELETE_URL))

    def test_template_name_correct(self, auto_login_user):
        client, user = auto_login_user()
        response = client.get(ACCOUNT_DELETE_URL)

        assertTemplateUsed(response, "account/account_delete.html")

    def test_form_class_correct(self, auto_login_user):
        client, user = auto_login_user()
        response = client.get(ACCOUNT_DELETE_URL)

        assert isinstance(response.context["form"], AccountDeleteForm)

    def test_success_url(self, auto_login_user):
        client, user = auto_login_user()
        response = client.post(ACCOUNT_DELETE_URL, data={"password": "test123"})

        assertRedirects(response, reverse("pastes:create"))

    def test_can_delete_account(self, auto_login_user):
        client, user = auto_login_user()
        client.post(ACCOUNT_DELETE_URL, data={"password": "test123"})

        assert User.objects.count() == 0

    def test_cannot_delete_account_when_password_incorrect(self, auto_login_user):
        client, user = auto_login_user()
        client.post(ACCOUNT_DELETE_URL, data={"password": "incorrect_pass"})

        assert User.objects.count() == 1


class TestPreferencesEdit:
    def test_login_required(self, client):
        response = client.get(PREFERENCES_UPDATE_URL)

        assertRedirects(response, login_redirect_url(PREFERENCES_UPDATE_URL))

    def test_template_name_correct(self, auto_login_user):
        client, user = auto_login_user()
        response = client.get(PREFERENCES_UPDATE_URL)

        assertTemplateUsed(response, "account/preferences.html")

    def test_form_class_correct(self, auto_login_user):
        client, user = auto_login_user()
        response = client.get(PREFERENCES_UPDATE_URL)

        assert isinstance(response.context["form"], PreferencesForm)

    def test_success_url(self, auto_login_user):
        client, user = auto_login_user()
        data = {
            "default_syntax": "python",
            "default_expiration_symbol": Preferences.TEN_MINUTES,
            "default_exposure": Preferences.Exposure.PRIVATE,
            "layout_width": Preferences.LayoutWidth.WIDE,
        }
        response = client.post(PREFERENCES_UPDATE_URL, data=data)

        assertRedirects(response, PREFERENCES_UPDATE_URL)

    def test_can_update_preferences(self, auto_login_user):
        client, user = auto_login_user()
        data = {
            "default_syntax": "python",
            "default_expiration_symbol": Preferences.TEN_MINUTES,
            "default_exposure": Preferences.Exposure.PRIVATE,
            "layout_width": Preferences.LayoutWidth.WIDE,
        }
        client.post(PREFERENCES_UPDATE_URL, data=data)
        user.refresh_from_db()

        assert user.preferences.default_syntax == "python"
        assert user.preferences.default_expiration_symbol == Preferences.TEN_MINUTES
        assert user.preferences.default_exposure == Preferences.Exposure.PRIVATE
        assert user.preferences.layout_width == Preferences.LayoutWidth.WIDE
