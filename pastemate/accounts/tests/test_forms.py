import pytest
from django.contrib.auth import get_user_model
from django.http import HttpRequest

from pastemate.accounts.forms import AccountDeleteForm

User = get_user_model()

pytestmark = pytest.mark.django_db


@pytest.fixture
def user():
    return User.objects.create_user(
        username="Test", email="test@test.com", password="test123"
    )


def test_form_raises_error_when_password_incorrect(user):
    request = HttpRequest()
    request.user = user
    form = AccountDeleteForm(request=request, data={"password": "incorrect_pass"})

    assert form.errors["password"] == ["Entered password is invalid."]


def test_form_is_valid_when_password_correct(user):
    request = HttpRequest()
    request.user = user
    form = AccountDeleteForm(request=request, data={"password": "test123"})

    assert form.is_valid()
