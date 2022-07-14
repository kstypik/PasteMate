import pytest
from django.urls import reverse
from pytest_django.asserts import (
    assertContains,
    assertNotContains,
    assertRedirects,
    assertTemplateUsed,
)

from pastemate.pastes import forms
from pastemate.pastes.models import Paste

pytestmark = pytest.mark.django_db


@pytest.fixture
def create_paste_with_detail_with_password_url(create_paste_with_url):
    def make_paste_with_detail_with_password_url(**kwargs):
        return create_paste_with_url(viewname="pastes:detail_with_password", **kwargs)

    return make_paste_with_detail_with_password_url


def test_template_name_correct(client, create_paste_with_detail_with_password_url):
    paste, url = create_paste_with_detail_with_password_url(password="pass123")
    response = client.get(url)

    assertTemplateUsed(response, "pastes/detail.html")


def test_password_form_in_context(client, create_paste_with_detail_with_password_url):
    paste, url = create_paste_with_detail_with_password_url(password="pass123")
    response = client.get(url)
    form = response.context["password_form"]

    assert isinstance(form, forms.PasswordProtectedPasteForm)


def test_password_protected_in_context(
    client, create_paste_with_detail_with_password_url
):
    paste, url = create_paste_with_detail_with_password_url(password="pass123")
    response = client.get(url)

    assert response.context["password_protected"]


def test_redirects_to_normal_detail_on_GET_when_paste_has_no_password(
    client, create_paste
):
    paste_without_pass = create_paste()

    response = client.get(
        reverse("pastes:detail_with_password", args=[paste_without_pass.uuid])
    )

    assertRedirects(response, paste_without_pass.get_absolute_url())


def test_redirects_to_normal_detail_on_POST_when_paste_has_no_password(
    create_paste, client
):
    paste_without_pass = create_paste()

    response = client.post(
        reverse("pastes:detail_with_password", args=[paste_without_pass.uuid])
    )

    assertRedirects(response, paste_without_pass.get_absolute_url())


def test_can_access_paste_when_submitted_password_correct(
    client, create_paste_with_detail_with_password_url
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
    client, create_paste_with_detail_with_password_url
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
    client, create_paste_with_detail_with_password_url
):
    paste, url = create_paste_with_detail_with_password_url(password="pass")

    response = client.get(url)

    assertNotContains(response, paste.content)


def test_can_burn_paste_when_also_password_protected(client, create_paste):
    burnable_paste_with_pass = create_paste(burn_after_read=True, password="pass123")
    burnable_paste_uuid = burnable_paste_with_pass.uuid
    paste_url = reverse(
        "pastes:detail_with_password", args=[burnable_paste_with_pass.uuid]
    )

    client.post(paste_url, data={"password": "pass123"})

    assert not Paste.objects.filter(uuid=burnable_paste_uuid).exists()


def test_cannot_burn_paste_with_password_when_wrong_password_provided(
    client, create_paste
):
    burnable_paste_with_pass = create_paste(burn_after_read=True, password="pass123")
    burnable_paste_uuid = burnable_paste_with_pass.uuid
    paste_url = reverse(
        "pastes:detail_with_password", args=[burnable_paste_with_pass.uuid]
    )

    client.post(paste_url, data={"password": "wrong"})

    assert Paste.objects.filter(uuid=burnable_paste_uuid).exists()


def test_cannot_burn_paste_with_password_on_GET(client, create_paste):
    burnable_paste_with_pass = create_paste(burn_after_read=True, password="pass123")
    burnable_paste_uuid = burnable_paste_with_pass.uuid
    paste_url = reverse(
        "pastes:detail_with_password", args=[burnable_paste_with_pass.uuid]
    )

    client.get(paste_url)

    assert Paste.objects.filter(uuid=burnable_paste_uuid).exists()
