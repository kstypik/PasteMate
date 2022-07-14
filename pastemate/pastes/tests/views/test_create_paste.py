from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from pytest_django.asserts import assertContains, assertRedirects, assertTemplateUsed

from pastemate.pastes import forms
from pastemate.pastes.models import Paste

pytestmark = pytest.mark.django_db

User = get_user_model()

PASTE_CREATE_URL = reverse("pastes:create")


def test_template_name_correct(client):
    response = client.get(PASTE_CREATE_URL)

    assertTemplateUsed(response, "pastes/form.html")


def test_form_class_correct(client):
    response = client.get(PASTE_CREATE_URL)

    assert isinstance(response.context["form"], forms.PasteForm)


def test_action_type_in_template(client):
    action_type = "Create New Paste"

    response = client.get(PASTE_CREATE_URL)

    assertContains(response, action_type)


@patch("hcaptcha_field.fields.hCaptchaField.validate", return_value=True)
def test_success_url(mock, client):
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
def test_guest_can_create_paste(mock, client):
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


def test_user_can_create_paste(auto_login_user):
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
