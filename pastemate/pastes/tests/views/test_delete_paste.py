import pytest
from pytest_django.asserts import assertRedirects, assertTemplateUsed

from pastemate.pastes.models import Paste

pytestmark = pytest.mark.django_db


@pytest.fixture
def create_paste_with_delete_url(create_paste_with_url):
    def make_paste_with_delete_url(**kwargs):
        return create_paste_with_url(viewname="pastes:delete", **kwargs)

    return make_paste_with_delete_url


def test_template_name_correct(auto_login_user, create_paste_with_delete_url):
    client, user = auto_login_user()
    paste, url = create_paste_with_delete_url(author=user)

    response = client.get(url)

    assertTemplateUsed(response, "pastes/delete.html")


def test_cannot_delete_if_not_paste_author(
    create_user, user, client, create_paste_with_delete_url
):
    paste, url = create_paste_with_delete_url(author=user)
    another_user = create_user()
    client.force_login(another_user)

    response = client.get(url)

    assert response.status_code == 404


def test_can_delete_paste(auto_login_user, create_paste_with_delete_url):
    client, user = auto_login_user()
    paste, url = create_paste_with_delete_url(author=user)

    client.post(url)

    assert Paste.objects.count() == 0


def test_redirects_to_homepage_after_successful_delete(
    auto_login_user, create_paste_with_delete_url
):
    client, user = auto_login_user()
    paste, url = create_paste_with_delete_url(author=user)

    response = client.post(url)

    assertRedirects(response, "/")
