import pytest

from pastemate.accounts.models import User
from pastemate.pastes.models import Paste


@pytest.fixture
def create_paste():
    def paste(
        content="Hello World",
        title="Should be linked",
        syntax="text",
        expiration_date=None,
        author=None,
        password="",
        burn_after_read=False,
        exposure=Paste.Exposure.PUBLIC,
        expiration_symbol=Paste.NEVER,
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
        )

    return paste


@pytest.fixture
def user():
    return User.objects.create_user(username="John")
