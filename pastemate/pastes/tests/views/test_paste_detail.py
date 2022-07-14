import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import formats
from pytest_django.asserts import (
    assertContains,
    assertInHTML,
    assertNotContains,
    assertRedirects,
    assertTemplateUsed,
)

from pastemate.pastes.models import Paste

pytestmark = pytest.mark.django_db

User = get_user_model()


@pytest.fixture
def create_paste_with_detail_url(create_paste_with_url):
    def make_paste_with_detail_url(**kwargs):
        return create_paste_with_url(viewname="pastes:detail", **kwargs)

    return make_paste_with_detail_url


def test_template_name_correct(create_paste_with_detail_url, client):
    paste, url = create_paste_with_detail_url()

    response = client.get(url)

    assertTemplateUsed(response, "pastes/detail.html")


def test_redirects_pastes_with_passwords_to_appropriate_view(create_paste, client):
    paste_with_pass = create_paste(password="pass")

    response = client.get(paste_with_pass.get_absolute_url())

    assertRedirects(
        response,
        reverse("pastes:detail_with_password", args=[paste_with_pass.uuid]),
    )


def test_can_burn_paste(client, create_paste):
    burnable_paste = create_paste(burn_after_read=True)
    burnable_paste_uuid = burnable_paste.uuid

    client.post(burnable_paste.get_absolute_url())

    assert not Paste.objects.filter(uuid=burnable_paste_uuid).exists()


def test_displays_private_message_to_author_url_for_logged(
    auto_login_user, create_paste_with_detail_url, create_user
):
    client, logged_user = auto_login_user()
    user = create_user()
    paste, url = create_paste_with_detail_url(author=user)

    response = client.get(url)

    pm_url = reverse("pinax_messages:message_user_create", args=[user.id])
    assertContains(response, pm_url)


def test_does_not_display_private_message_to_author_url_for_themselves(
    client, user, create_paste
):
    paste_with_author = create_paste(author=user)

    response = client.get(paste_with_author.get_absolute_url())

    pm_url = reverse("pinax_messages:message_user_create", args=[user.id])
    assertNotContains(response, pm_url)


def test_does_not_display_private_message_to_author_url_for_unlogged(
    client, user, create_paste_with_detail_url
):
    paste, url = create_paste_with_detail_url(author=user)

    response = client.get(url)

    pm_url = reverse("pinax_messages:message_user_create", args=[user.id])
    assertNotContains(response, pm_url)


def test_displays_correct_expiration_date_when_set(
    create_paste_with_detail_url, client
):
    paste, url = create_paste_with_detail_url(expiration_symbol=Paste.TEN_MINUTES)

    response = client.get(url)

    expiration_date = formats.date_format(paste.expiration_date, "c")
    html = (
        f'<span class="to-relative-datetime text-capitalize">{expiration_date}</span>'
    )
    assertInHTML(html, response.content.decode("utf-8"))


def test_displays_authors_location_when_set(client, create_paste_with_detail_url, user):
    paste, url = create_paste_with_detail_url(author=user)

    response = client.get(url)

    assertContains(response, user.location)


def test_displays_authors_website_when_set(client, user, create_paste_with_detail_url):
    paste, url = create_paste_with_detail_url(author=user)

    response = client.get(url)

    assertContains(response, user.website)
