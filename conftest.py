import pytest

from pastemate.pastes.models import Paste


@pytest.fixture
def create_paste():
    def paste(content="Hello World", title="Should be linked", expiration_date=None):
        return Paste.objects.create(
            content=content, title=title, expiration_date=expiration_date
        )

    return paste
