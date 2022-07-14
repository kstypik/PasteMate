import pytest
from django.test import override_settings
from django.urls import reverse
from django.utils import formats
from pytest_django.asserts import assertContains, assertInHTML, assertTemplateUsed

from pastemate.pastes.models import Paste

pytestmark = pytest.mark.django_db


def test_template_name_correct(auto_login_user):
    client, user = auto_login_user()

    response = client.get(reverse("pastes:user_pastes", args=[user.username]))

    assertTemplateUsed(response, "pastes/user_list.html")


def test_user_can_see_their_own_pastes(auto_login_user, create_paste):
    client, user = auto_login_user()
    public_paste = create_paste(author=user, exposure=Paste.Exposure.PUBLIC)
    unlisted_paste = create_paste(author=user, exposure=Paste.Exposure.UNLISTED)
    private_paste = create_paste(author=user, exposure=Paste.Exposure.PRIVATE)

    response = client.get(reverse("pastes:user_pastes", args=[user.username]))

    assert public_paste in response.context["page_obj"]
    assert unlisted_paste in response.context["page_obj"]
    assert private_paste in response.context["page_obj"]


def test_others_cannot_see_users_nonpublic_pastes(client, user, create_paste):
    public_paste = create_paste(author=user, exposure=Paste.Exposure.PUBLIC)
    unlisted_paste = create_paste(author=user, exposure=Paste.Exposure.UNLISTED)
    private_paste = create_paste(author=user, exposure=Paste.Exposure.PRIVATE)

    response = client.get(reverse("pastes:user_pastes", args=[user.username]))

    assert public_paste in response.context["page_obj"]
    assert unlisted_paste not in response.context["page_obj"]
    assert private_paste not in response.context["page_obj"]


def test_user_can_see_their_list_as_guest(auto_login_user, create_paste):
    client, user = auto_login_user()
    public_paste = create_paste(author=user, exposure=Paste.Exposure.PUBLIC)
    unlisted_paste = create_paste(author=user, exposure=Paste.Exposure.UNLISTED)
    private_paste = create_paste(author=user, exposure=Paste.Exposure.PRIVATE)

    response = client.get(
        reverse("pastes:user_pastes", args=[user.username]), {"guest": "1"}
    )

    assert public_paste in response.context["page_obj"]
    assert unlisted_paste not in response.context["page_obj"]
    assert private_paste not in response.context["page_obj"]


def test_user_can_see_their_folders_on_list(auto_login_user, create_folder):
    client, user = auto_login_user()
    folder1 = create_folder(name="Folder 1", created_by=user)
    folder2 = create_folder(name="Folder 2", created_by=user)

    response = client.get(reverse("pastes:user_pastes", args=[user.username]))

    assert folder1 in response.context["folders"]
    assert folder2 in response.context["folders"]


def test_show_count_of_pastes_in_folder(auto_login_user, create_folder, create_paste):
    client, user = auto_login_user()
    folder1 = create_folder(name="Folder 1", created_by=user)
    folder2 = create_folder(name="Folder 2", created_by=user)
    create_folder(name="Folder 3", created_by=user)
    create_paste(folder=folder1)
    create_paste(folder=folder1)
    create_paste(folder=folder2)

    response = client.get(reverse("pastes:user_pastes", args=[user.username]))

    assert response.context["folders"].get(name="Folder 1").num_pastes == 2
    assert response.context["folders"].get(name="Folder 2").num_pastes == 1
    assert response.context["folders"].get(name="Folder 3").num_pastes == 0


def test_user_cannot_see_other_users_folders_on_list(
    create_folder, user, client, create_user
):
    folder1 = create_folder(name="Folder 1", created_by=user)
    folder2 = create_folder(name="Folder 2", created_by=user)
    another_user = create_user()
    client.force_login(another_user)

    response = client.get(reverse("pastes:user_pastes", args=[another_user.username]))

    assert folder1 not in response.context["folders"]
    assert folder2 not in response.context["folders"]


@override_settings(PASTES_USER_LIST_PAGINATE_BY=2)
def test_user_list_is_paginated(create_paste, auto_login_user):
    client, user = auto_login_user()
    for _ in range(10):
        create_paste(author=user)

    response = client.get(reverse("pastes:user_pastes", args=[user.username]))

    assert response.context["page_obj"].paginator.num_pages == 5


def test_show_statistics(create_paste, auto_login_user):
    client, user = auto_login_user()
    for _ in range(2):
        create_paste(author=user, exposure="PU")
    for _ in range(4):
        create_paste(author=user, exposure="UN")
    for _ in range(3):
        create_paste(author=user, exposure="PR")

    response = client.get(reverse("pastes:user_pastes", args=[user.username]))

    stats = response.context["stats"]
    assert stats["total_pastes"] == 9
    assert stats["public_pastes"] == 2
    assert stats["unlisted_pastes"] == 4
    assert stats["private_pastes"] == 3


def test_displays_correct_expiration_date_when_set(auto_login_user, create_paste):
    client, user = auto_login_user()
    expiring_paste = create_paste(expiration_symbol=Paste.TEN_MINUTES, author=user)

    response = client.get(reverse("pastes:user_pastes", args=[user.username]))

    expiration_date = formats.date_format(expiring_paste.expiration_date, "c")
    html = f'<span class="to-relative-datetime">{expiration_date}</span>'
    assertInHTML(html, response.content.decode("utf-8"))


def test_displays_authors_location_when_set(auto_login_user):
    client, user = auto_login_user()

    response = client.get(reverse("pastes:user_pastes", args=[user.username]))

    assertContains(response, user.location)


def test_displays_authors_website_when_set(auto_login_user):
    client, user = auto_login_user()

    response = client.get(reverse("pastes:user_pastes", args=[user.username]))

    html = f'<a href="{user.website}">{user.website}</a>'
    assertInHTML(html, response.content.decode("utf-8"))
