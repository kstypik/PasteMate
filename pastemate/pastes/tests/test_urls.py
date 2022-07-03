import uuid

from django.test import SimpleTestCase
from django.urls import resolve, reverse

UID = uuid.uuid4()


class PasteUrlsTest(SimpleTestCase):
    def test_archive(self):
        self.assertEqual(reverse("pastes:archive"), "/archive/")
        self.assertEqual(resolve("/archive/").view_name, "pastes:archive")

    def test_syntax_archive(self):

        self.assertEqual(
            reverse("pastes:syntax_archive", kwargs={"syntax": "python"}),
            "/archive/python/",
        )
        self.assertEqual(resolve("/archive/python/").view_name, "pastes:syntax_archive")

    def test_syntax_languages(self):
        self.assertEqual(reverse("pastes:syntax_languages"), "/languages/")
        self.assertEqual(resolve("/languages/").view_name, "pastes:syntax_languages")

    def test_search(self):
        self.assertEqual(reverse("pastes:search"), "/search/")
        self.assertEqual(resolve("/search/").view_name, "pastes:search")

    def test_backup(self):
        self.assertEqual(reverse("pastes:backup"), "/backup/")
        self.assertEqual(resolve("/backup/").view_name, "pastes:backup")

    def test_user_pastes(self):
        self.assertEqual(
            reverse("pastes:user_pastes", kwargs={"username": "test"}),
            "/user/test/",
        )
        self.assertEqual(resolve("/user/test/").view_name, "pastes:user_pastes")

    def test_user_folder(self):
        self.assertEqual(
            reverse(
                "pastes:user_folder",
                kwargs={"username": "test", "folder_slug": "folder-test"},
            ),
            "/user/test/folder/folder-test/",
        )
        self.assertEqual(
            resolve("/user/test/folder/folder-test/").view_name,
            "pastes:user_folder",
        )

    def test_user_folder_edit(self):
        self.assertEqual(
            reverse(
                "pastes:user_folder_edit",
                kwargs={"username": "test", "folder_slug": "folder-test"},
            ),
            "/user/test/folder/folder-test/edit/",
        )
        self.assertEqual(
            resolve("/user/test/folder/folder-test/edit/").view_name,
            "pastes:user_folder_edit",
        )

    def test_user_folder_delete(self):
        self.assertEqual(
            reverse(
                "pastes:user_folder_delete",
                kwargs={"username": "test", "folder_slug": "folder-test"},
            ),
            "/user/test/folder/folder-test/delete/",
        )
        self.assertEqual(
            resolve("/user/test/folder/folder-test/delete/").view_name,
            "pastes:user_folder_delete",
        )

    def test_detail(self):
        self.assertEqual(
            reverse(
                "pastes:detail",
                kwargs={
                    "uuid": UID,
                },
            ),
            f"/{UID}/",
        )
        self.assertEqual(
            resolve(f"/{UID}/").view_name,
            "pastes:detail",
        )

    def test_raw_detail(self):
        self.assertEqual(
            reverse(
                "pastes:raw_detail",
                kwargs={
                    "uuid": UID,
                },
            ),
            f"/{UID}/raw/",
        )
        self.assertEqual(
            resolve(f"/{UID}/raw/").view_name,
            "pastes:raw_detail",
        )

    def test_paste_download(self):
        self.assertEqual(
            reverse(
                "pastes:paste_download",
                kwargs={
                    "uuid": UID,
                },
            ),
            f"/{UID}/dl/",
        )
        self.assertEqual(
            resolve(f"/{UID}/dl/").view_name,
            "pastes:paste_download",
        )

    def test_clone(self):
        self.assertEqual(
            reverse(
                "pastes:clone",
                kwargs={
                    "uuid": UID,
                },
            ),
            f"/{UID}/clone/",
        )
        self.assertEqual(
            resolve(f"/{UID}/clone/").view_name,
            "pastes:clone",
        )

    def test_embed(self):
        self.assertEqual(
            reverse(
                "pastes:embed",
                kwargs={
                    "uuid": UID,
                },
            ),
            f"/{UID}/embed/",
        )
        self.assertEqual(
            resolve(f"/{UID}/embed/").view_name,
            "pastes:embed",
        )

    def test_print(self):
        self.assertEqual(
            reverse(
                "pastes:print",
                kwargs={
                    "uuid": UID,
                },
            ),
            f"/{UID}/print/",
        )
        self.assertEqual(
            resolve(f"/{UID}/print/").view_name,
            "pastes:print",
        )

    def test_report(self):
        self.assertEqual(
            reverse(
                "pastes:report",
                kwargs={
                    "uuid": UID,
                },
            ),
            f"/{UID}/report/",
        )
        self.assertEqual(
            resolve(f"/{UID}/report/").view_name,
            "pastes:report",
        )

    def test_detail_with_password(self):
        self.assertEqual(
            reverse(
                "pastes:detail_with_password",
                kwargs={
                    "uuid": UID,
                },
            ),
            f"/{UID}/pass/",
        )
        self.assertEqual(
            resolve(f"/{UID}/pass/").view_name,
            "pastes:detail_with_password",
        )

    def test_update(self):
        self.assertEqual(
            reverse(
                "pastes:update",
                kwargs={
                    "uuid": UID,
                },
            ),
            f"/{UID}/edit/",
        )
        self.assertEqual(
            resolve(f"/{UID}/edit/").view_name,
            "pastes:update",
        )

    def test_delete(self):
        self.assertEqual(
            reverse(
                "pastes:delete",
                kwargs={
                    "uuid": UID,
                },
            ),
            f"/{UID}/delete/",
        )
        self.assertEqual(
            resolve(f"/{UID}/delete/").view_name,
            "pastes:delete",
        )
