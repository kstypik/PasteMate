import uuid

import pytest

from pastemate.accounts.models import User
from pastemate.pastes.models import Paste


@pytest.fixture
def create_paste():
    def paste(
        content="Hello World",
        title="Paste For Testing",
        syntax="text",
        expiration_date=None,
        author=None,
        password="",
        burn_after_read=False,
        exposure=Paste.Exposure.PUBLIC,
        expiration_symbol=Paste.NEVER,
        folder=None,
    ):
        return Paste.objects.create(
            content=content,
            title=title,
            expiration_date=expiration_date,
            syntax=syntax,
            author=author,
            password=password,
            burn_after_read=burn_after_read,
            exposure=exposure,
            expiration_symbol=expiration_symbol,
            folder=folder,
        )

    return paste


@pytest.fixture
def user():
    return User.objects.create_user(
        username="John",
        password="test123",
        location="Testland",
        website="https://example.com",
    )


@pytest.fixture
def create_user():
    def make_user(username=None, email=None, **kwargs):
        if username is None:
            kwargs.update({"username": uuid.uuid4()})
        if email is None:
            kwargs.update({"email": f"{uuid.uuid4()}@test.com"})
        return User.objects.create_user(**kwargs)

    return make_user


@pytest.fixture
def auto_login_user(db, client, user):
    def make_auto_login(user_obj=None):
        if user_obj is None:
            user_obj = user
        client.force_login(user_obj)
        return client, user_obj

    return make_auto_login
