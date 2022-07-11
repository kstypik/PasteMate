import uuid

from django.urls import resolve, reverse

UID = uuid.uuid4()


def test_archive():
    assert reverse("pastes:archive") == "/archive/"
    assert resolve("/archive/").view_name == "pastes:archive"


def test_syntax_archive():

    assert (
        reverse("pastes:syntax_archive", kwargs={"syntax": "python"})
        == "/archive/python/"
    )
    assert resolve("/archive/python/").view_name == "pastes:syntax_archive"


def test_syntax_languages():
    assert reverse("pastes:syntax_languages") == "/languages/"
    assert resolve("/languages/").view_name == "pastes:syntax_languages"


def test_search():
    assert reverse("pastes:search") == "/search/"
    assert resolve("/search/").view_name == "pastes:search"


def test_backup():
    assert reverse("pastes:backup") == "/backup/"
    assert resolve("/backup/").view_name == "pastes:backup"


def test_user_pastes():
    assert reverse("pastes:user_pastes", kwargs={"username": "test"}) == "/user/test/"
    assert resolve("/user/test/").view_name == "pastes:user_pastes"


def test_user_folder():
    assert (
        reverse(
            "pastes:user_folder",
            kwargs={"username": "test", "folder_slug": "folder-test"},
        )
        == "/user/test/folder/folder-test/"
    )
    assert resolve("/user/test/folder/folder-test/").view_name == "pastes:user_folder"


def test_user_folder_edit():
    assert (
        reverse(
            "pastes:user_folder_edit",
            kwargs={"username": "test", "folder_slug": "folder-test"},
        )
        == "/user/test/folder/folder-test/edit/"
    )
    assert (
        resolve("/user/test/folder/folder-test/edit/").view_name
        == "pastes:user_folder_edit"
    )


def test_user_folder_delete():
    assert (
        reverse(
            "pastes:user_folder_delete",
            kwargs={"username": "test", "folder_slug": "folder-test"},
        )
        == "/user/test/folder/folder-test/delete/"
    )
    assert (
        resolve("/user/test/folder/folder-test/delete/").view_name
        == "pastes:user_folder_delete"
    )


def test_detail():
    assert (
        reverse(
            "pastes:detail",
            kwargs={
                "uuid": UID,
            },
        )
        == f"/{UID}/"
    )
    assert resolve(f"/{UID}/").view_name == "pastes:detail"


def test_raw_detail():
    assert (
        reverse(
            "pastes:raw_detail",
            kwargs={
                "uuid": UID,
            },
        )
        == f"/{UID}/raw/"
    )
    assert resolve(f"/{UID}/raw/").view_name == "pastes:raw_detail"


def test_paste_download():
    assert (
        reverse(
            "pastes:paste_download",
            kwargs={
                "uuid": UID,
            },
        )
        == f"/{UID}/dl/"
    )
    assert resolve(f"/{UID}/dl/").view_name == "pastes:paste_download"


def test_clone():
    assert (
        reverse(
            "pastes:clone",
            kwargs={
                "paste_uuid": UID,
            },
        )
        == f"/{UID}/clone/"
    )
    assert resolve(f"/{UID}/clone/").view_name == "pastes:clone"


def test_embed():
    assert (
        reverse(
            "pastes:embed",
            kwargs={
                "uuid": UID,
            },
        )
        == f"/{UID}/embed/"
    )
    assert resolve(f"/{UID}/embed/").view_name == "pastes:embed"


def test_print():
    assert (
        reverse(
            "pastes:print",
            kwargs={
                "uuid": UID,
            },
        )
        == f"/{UID}/print/"
    )
    assert resolve(f"/{UID}/print/").view_name == "pastes:print"


def test_report():
    assert (
        reverse(
            "pastes:report",
            kwargs={
                "uuid": UID,
            },
        )
        == f"/{UID}/report/"
    )
    assert resolve(f"/{UID}/report/").view_name == "pastes:report"


def test_detail_with_password():
    assert (
        reverse(
            "pastes:detail_with_password",
            kwargs={
                "uuid": UID,
            },
        )
        == f"/{UID}/pass/"
    )
    assert resolve(f"/{UID}/pass/").view_name == "pastes:detail_with_password"


def test_update():
    assert (
        reverse(
            "pastes:update",
            kwargs={
                "uuid": UID,
            },
        )
        == f"/{UID}/edit/"
    )
    assert resolve(f"/{UID}/edit/").view_name == "pastes:update"


def test_delete():
    assert (
        reverse(
            "pastes:delete",
            kwargs={
                "uuid": UID,
            },
        )
        == f"/{UID}/delete/"
    )
    assert resolve(f"/{UID}/delete/").view_name == "pastes:delete"
