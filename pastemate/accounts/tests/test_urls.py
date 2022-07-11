from django.urls import resolve, reverse


def test_profile_update():
    assert reverse("accounts:profile_update") == "/accounts/edit-profile/"
    assert resolve("/accounts/edit-profile/").view_name == "accounts:profile_update"


def test_delete():
    assert reverse("accounts:delete") == "/accounts/delete/"
    assert resolve("/accounts/delete/").view_name == "accounts:delete"


def test_preferences():
    assert reverse("accounts:preferences") == "/accounts/preferences/"
    assert resolve("/accounts/preferences/").view_name == "accounts:preferences"


def test_avatar():
    assert reverse("accounts:avatar") == "/accounts/avatar/"
    assert resolve("/accounts/avatar/").view_name == "accounts:avatar"
