import pytest
from django.contrib.auth import get_user_model
from pytest_django.asserts import assertContains, assertRedirects

from pastemate.core.utils import login_redirect_url
from pastemate.pastes.models import Paste

pytestmark = pytest.mark.django_db

User = get_user_model()


@pytest.fixture
def create_paste_with_copied_url(create_paste_with_url):
    def make_paste_with_copied_url(**kwargs):
        return create_paste_with_url(viewname="pastes:clone", **kwargs)

    return make_paste_with_copied_url


def test_action_type_in_template(auto_login_user, create_paste_with_copied_url):
    paste, url = create_paste_with_copied_url()
    client, user = auto_login_user()
    action_type = "Clone Paste"

    response = client.get(url)

    assertContains(response, action_type)


def test_login_required(client, create_paste_with_copied_url):
    paste, url = create_paste_with_copied_url()

    response = client.get(url)

    assertRedirects(response, login_redirect_url(url))


def test_correct_initial_data(auto_login_user, create_paste_with_copied_url):
    paste, url = create_paste_with_copied_url()
    client, user = auto_login_user()

    response = client.get(url)

    form = response.context["form"]
    assert form.initial["content"] == paste.content
    assert form.initial["syntax"] == paste.syntax
    assert form.initial["title"] == paste.title


def test_can_clone_paste_with_default_data(
    auto_login_user, create_paste_with_copied_url
):
    paste, url = create_paste_with_copied_url()
    client, user = auto_login_user()

    data = {
        "content": paste.content,
        "title": paste.title,
        "syntax": paste.syntax,
        "exposure": "PU",
    }
    client.post(url, data=data)
    created_paste = Paste.objects.first()

    assert Paste.objects.count() == 2
    assert created_paste.content == paste.content
    assert created_paste.syntax == paste.syntax
    assert created_paste.title == paste.title


def test_can_clone_paste_with_custom_data(
    auto_login_user, create_paste_with_copied_url
):
    cloned_paste, url = create_paste_with_copied_url()
    client, user = auto_login_user()

    data = {
        "title": "My Cloned Paste",
        "syntax": "python",
        "content": "print('Hello World')",
        "exposure": "PU",
    }
    client.post(url, data=data)
    created_paste = Paste.objects.first()

    assert Paste.objects.count() == 2
    assert created_paste.content == "print('Hello World')"
    assert created_paste.syntax == "python"
    assert created_paste.title == "My Cloned Paste"


def test_cannot_clone_private_paste(auto_login_user, create_paste_with_copied_url):
    private_paste, url = create_paste_with_copied_url(exposure=Paste.Exposure.PRIVATE)
    client, user = auto_login_user()

    response = client.get(url)

    assert response.status_code == 404
