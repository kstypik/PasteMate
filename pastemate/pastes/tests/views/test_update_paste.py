import pytest
from pytest_django.asserts import assertContains, assertRedirects, assertTemplateUsed

from pastemate.pastes import forms

pytestmark = pytest.mark.django_db


@pytest.fixture
def create_paste_with_update_url(create_paste_with_url):
    def make_paste_with_update_url(**kwargs):
        return create_paste_with_url(viewname="pastes:update", **kwargs)

    return make_paste_with_update_url


def test_template_name_correct(auto_login_user, create_paste_with_update_url):
    client, user = auto_login_user()
    paste, url = create_paste_with_update_url(author=user)

    response = client.get(url)

    assertTemplateUsed(response, "pastes/form.html")


def test_form_in_context(auto_login_user, create_paste_with_update_url):
    client, user = auto_login_user()
    paste, url = create_paste_with_update_url(author=user)

    response = client.get(url)
    form = response.context["form"]

    assert isinstance(form, forms.PasteForm)


def test_cannot_update_if_not_paste_author(
    client, create_user, create_paste_with_update_url
):
    another_user = create_user()
    client.force_login(another_user)
    paste, url = create_paste_with_update_url()

    response = client.get(url)

    assert response.status_code == 404


def test_action_type_in_template(client, auto_login_user, create_paste_with_update_url):
    client, user = auto_login_user()
    paste, url = create_paste_with_update_url(author=user)
    action_type = "Edit"

    response = client.get(url)

    assertContains(response, action_type)


def test_can_update_paste(auto_login_user, create_paste_with_update_url):
    client, user = auto_login_user()
    paste, url = create_paste_with_update_url(author=user)
    data = {
        "content": "Hello Updated",
        "syntax": "html",
        "exposure": "PU",
    }

    client.post(url, data=data)
    paste.refresh_from_db()

    assert paste.content == "Hello Updated"
    assert paste.syntax == "html"


def test_redirects_to_paste_after_successful_update(
    auto_login_user, create_paste_with_update_url
):
    client, user = auto_login_user()
    paste, url = create_paste_with_update_url(author=user)
    data = {
        "content": "Hello Updated",
        "syntax": "html",
        "exposure": "PU",
    }

    response = client.post(url, data=data)

    assertRedirects(response, paste.get_absolute_url())
