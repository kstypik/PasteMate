import pytest
from django.urls import reverse
from pytest_django.asserts import assertTemplateUsed

from pastemate.pastes.models import Paste

pytestmark = pytest.mark.django_db


def test_template_name_correct(client, create_paste):
    paste = create_paste()
    print_url = reverse("pastes:print", args=[paste.uuid])

    response = client.get(print_url)

    assertTemplateUsed(response, "pastes/print.html")


def test_print_window_is_loaded(client, create_paste):
    paste = create_paste()
    print_url = reverse("pastes:print", args=[paste.uuid])

    response = client.get(print_url)

    html = '<body onload="window.print()">'
    assert html in response.content.decode("utf-8")


def test_displays_content_html(client, create_paste):
    paste = create_paste()
    print_url = reverse("pastes:print", args=[paste.uuid])

    response = client.get(print_url)

    assert paste.content_html in response.content.decode("utf-8")


def test_cannot_print_burnable_paste(create_paste, client):
    burnable_paste = create_paste(burn_after_read=True)
    print_url = reverse("pastes:print", args=[burnable_paste.uuid])

    response = client.get(print_url)

    assert response.status_code == 404


def test_cannot_print_password_protected_paste(create_paste, client):
    paste_with_pass = create_paste(password="pass123")
    print_url = reverse("pastes:print", args=[paste_with_pass.uuid])

    response = client.get(print_url)

    assert response.status_code == 404


def test_cannot_print_private_paste(client, create_paste):
    private_paste = create_paste(exposure=Paste.Exposure.PRIVATE)
    print_url = reverse("pastes:print", args=[private_paste.uuid])

    response = client.get(print_url)

    assert response.status_code == 404


def test_can_print_private_paste_if_its_author(create_paste, auto_login_user):
    client, user = auto_login_user()
    paste = create_paste(author=user)
    print_url = reverse("pastes:print", args=[paste.uuid])

    response = client.get(print_url)

    assert response.status_code == 200
