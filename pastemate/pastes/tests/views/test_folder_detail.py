import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects, assertTemplateUsed

from pastemate.core.utils import login_redirect_url

pytestmark = pytest.mark.django_db


def test_template_name_correct(auto_login_user, create_folder):
    client, user = auto_login_user()
    folder = create_folder(created_by=user)

    response = client.get(
        reverse("pastes:user_folder", args=[user.username, folder.slug])
    )

    assertTemplateUsed(response, "pastes/user_list.html")


def test_folder_and_user_in_context(auto_login_user, create_folder):
    client, user = auto_login_user()
    folder = create_folder(created_by=user)

    response = client.get(
        reverse("pastes:user_folder", args=[user.username, folder.slug])
    )

    assert folder == response.context["folder"]
    assert user == response.context["author"]


def test_author_can_view_pastes_in_folder(auto_login_user, create_folder, create_paste):
    client, user = auto_login_user()
    folder = create_folder(created_by=user)
    for _ in range(5):
        create_paste(author=user, folder=folder)

    response = client.get(
        reverse("pastes:user_folder", args=[user.username, folder.slug])
    )

    assert len(response.context["page_obj"]) == 5


def test_user_cannot_view_folders_of_other_users(
    client, auto_login_user, create_folder, create_user
):
    client, user = auto_login_user()
    another_user = create_user()
    folder = create_folder(created_by=another_user)

    response = client.get(
        reverse("pastes:user_folder", args=[user.username, folder.slug])
    )

    assert response.status_code == 404


def test_login_required(client, user, create_folder):
    folder = create_folder(created_by=user)

    response = client.get(
        reverse("pastes:user_folder", args=[user.username, folder.slug])
    )

    assertRedirects(
        response,
        login_redirect_url(
            reverse("pastes:user_folder", args=[user.username, folder.slug])
        ),
    )
