import pytest

pytestmark = pytest.mark.django_db


class TestUser:
    def test___str__(self, user):
        assert user.__str__() == user.username
        assert str(user) == user.username

    def test_get_absolute_url(self, user):
        url = user.get_absolute_url()

        assert url == f"/user/{user.username}/"


class TestPreferences:
    def test___str__(self, user):
        assert user.preferences.__str__() == f"Preferences of {user.username}"
        assert str(user.preferences) == f"Preferences of {user.username}"
