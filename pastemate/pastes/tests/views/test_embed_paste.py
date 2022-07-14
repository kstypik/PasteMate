import pytest
from django.urls import reverse
from pytest_django.asserts import assertInHTML, assertTemplateUsed

from pastemate.pastes.models import Paste

pytestmark = pytest.mark.django_db


def test_template_name_correct(client, create_paste):
    paste = create_paste()
    embed_url = reverse("pastes:embed", args=[paste.uuid])

    response = client.get(embed_url)

    assertTemplateUsed(response, "pastes/embed.html")


def test_direct_link_to_image_in_context(client, create_paste):
    paste = create_paste()
    embed_url = reverse("pastes:embed", args=[paste.uuid])

    response = client.get(embed_url)

    assert (
        f"http://testserver/media/embed/{paste.uuid}.png"
        == response.context["direct_embed_link"]
    )


def test_embed_image_is_displayed(client, create_paste):
    paste = create_paste()
    embed_url = reverse("pastes:embed", args=[paste.uuid])

    response = client.get(embed_url)

    html = f'<img src="{paste.embeddable_image.url}" alt="Paste\'s content represented as an image">'
    assertInHTML(html, response.content.decode("utf-8"))


def test_cannot_embed_burnable_paste(client, create_paste):
    burnable_paste = create_paste(burn_after_read=True)
    embed_url = reverse("pastes:embed", args=[burnable_paste.uuid])

    response = client.get(embed_url)

    assert response.status_code == 404


def test_cannot_embed_password_protected_paste(create_paste, client):
    paste_with_pass = create_paste(password="pass123")
    embed_url = reverse("pastes:embed", args=[paste_with_pass.uuid])

    response = client.get(embed_url)

    assert response.status_code == 404


def test_cannot_embed_private_paste(create_paste, client):
    private_paste = create_paste(exposure=Paste.Exposure.PRIVATE)
    embed_url = reverse("pastes:embed", args=[private_paste.uuid])

    response = client.get(embed_url)

    assert response.status_code == 404


def test_author_cannot_embed_their_private_paste(auto_login_user, create_paste):
    client, user = auto_login_user()
    private_paste = create_paste(exposure=Paste.Exposure.PRIVATE, author=user)
    embed_url = reverse("pastes:embed", args=[private_paste.uuid])

    response = client.get(embed_url)

    assert response.status_code == 404
