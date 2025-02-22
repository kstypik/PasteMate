import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects, assertTemplateUsed

from pastes import forms

pytestmark = pytest.mark.django_db


def test_template_name_correct(auto_login_user, create_folder):
    client, user = auto_login_user()
    folder = create_folder(created_by=user)

    response = client.get(
        reverse("pastes:user_folder_edit", args=[user.username, folder.slug])
    )

    assertTemplateUsed(response, "pastes/folder_form.html")


def test_form_in_context(auto_login_user, create_folder):
    client, user = auto_login_user()
    folder = create_folder(created_by=user)

    response = client.get(
        reverse("pastes:user_folder_edit", args=[user.username, folder.slug])
    )
    form = response.context["form"]

    assert isinstance(form, forms.FolderForm)


def test_success_url(auto_login_user, create_folder):
    client, user = auto_login_user()
    folder = create_folder(created_by=user)
    data = {
        "name": "Updated",
    }

    response = client.post(
        reverse("pastes:user_folder_edit", args=[user.username, folder.slug]),
        data=data,
    )
    folder.refresh_from_db()

    assertRedirects(
        response,
        folder.get_absolute_url(),
    )


def test_folder_author_can_update_its_name(auto_login_user, create_folder):
    client, user = auto_login_user()
    folder = create_folder(created_by=user)
    data = {
        "name": "Updated",
    }

    client.post(
        reverse("pastes:user_folder_edit", args=[user.username, folder.slug]),
        data=data,
    )
    folder.refresh_from_db()

    assert folder.name == "Updated"


def test_user_cannot_update_another_users_folder(
    create_folder, client, create_user, auto_login_user
):
    data = {
        "name": "Updated",
    }
    client, user = auto_login_user()
    another_user = create_user()
    folder = create_folder(created_by=another_user)

    response = client.post(
        reverse("pastes:user_folder_edit", args=[user.username, folder.slug]),
        data=data,
    )
    folder.refresh_from_db()

    assert folder.name == "Testing folder"
    assert response.status_code == 404
