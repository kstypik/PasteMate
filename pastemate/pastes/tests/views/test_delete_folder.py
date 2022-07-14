import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects, assertTemplateUsed

from pastemate.pastes.models import Folder

pytestmark = pytest.mark.django_db


def test_template_name_correct(auto_login_user, create_folder):
    client, user = auto_login_user()
    folder = create_folder(created_by=user)

    response = client.get(
        reverse("pastes:user_folder_delete", args=[user.username, folder.slug])
    )

    assertTemplateUsed(response, "pastes/folder_delete.html")


def test_success_url(auto_login_user, create_folder):
    client, user = auto_login_user()
    folder = create_folder(created_by=user)

    response = client.post(
        reverse("pastes:user_folder_delete", args=[user.username, folder.slug])
    )

    assertRedirects(
        response,
        reverse("pastes:user_pastes", args=[user.username]),
    )


def test_folder_author_can_delete_folder(auto_login_user, create_folder):
    client, user = auto_login_user()
    folder = create_folder(created_by=user)

    client.post(reverse("pastes:user_folder_delete", args=[user.username, folder.slug]))

    assert Folder.objects.filter(created_by=user).count() == 0


def test_user_cannot_delete_another_users_folder(
    auto_login_user, create_folder, create_user
):
    client, user = auto_login_user()
    another_user = create_user()
    folder = create_folder(created_by=another_user)

    response = client.post(
        reverse("pastes:user_folder_delete", args=[user.username, folder.slug])
    )

    assert folder.name == "Testing folder"
    assert response.status_code == 404
