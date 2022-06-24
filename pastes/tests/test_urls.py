import random

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import resolve, reverse
from pastes.choices import get_all_languages
from pastes.models import Folder, Paste

User = get_user_model()


class PasteUrlsTest(TestCase):
    def test_archive(self):
        self.assertEqual(reverse("pastes:archive"), "/archive/")
        self.assertEqual(resolve("/archive/").view_name, "pastes:archive")

    def test_syntax_archive(self):
        language = random.choice(get_all_languages())[0]

        self.assertEqual(
            reverse("pastes:syntax_archive", kwargs={"syntax": language}),
            f"/archive/{language}/",
        )
        self.assertEqual(
            resolve(f"/archive/{language}/").view_name, "pastes:syntax_archive"
        )

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
        user = User.objects.create_user(username="Test")

        self.assertEqual(
            reverse("pastes:user_pastes", kwargs={"username": user.username}),
            f"/user/{user.username}/",
        )
        self.assertEqual(
            resolve(f"/user/{user.username}/").view_name, "pastes:user_pastes"
        )

    def test_user_folder(self):
        user = User.objects.create_user(username="Test")
        folder = Folder.objects.create(name="Testing folder", created_by=user)

        self.assertEqual(
            reverse(
                "pastes:user_folder",
                kwargs={"username": user.username, "folder_slug": folder.slug},
            ),
            f"/user/{user.username}/folder/{folder.slug}/",
        )
        self.assertEqual(
            resolve(f"/user/{user.username}/folder/{folder.slug}/").view_name,
            "pastes:user_folder",
        )

    def test_user_folder_edit(self):
        user = User.objects.create_user(username="Test")
        folder = Folder.objects.create(name="Testing folder", created_by=user)

        self.assertEqual(
            reverse(
                "pastes:user_folder_edit",
                kwargs={"username": user.username, "folder_slug": folder.slug},
            ),
            f"/user/{user.username}/folder/{folder.slug}/edit/",
        )
        self.assertEqual(
            resolve(f"/user/{user.username}/folder/{folder.slug}/edit/").view_name,
            "pastes:user_folder_edit",
        )

    def test_user_folder_delete(self):
        user = User.objects.create_user(username="Test")
        folder = Folder.objects.create(name="Testing folder", created_by=user)

        self.assertEqual(
            reverse(
                "pastes:user_folder_delete",
                kwargs={"username": user.username, "folder_slug": folder.slug},
            ),
            f"/user/{user.username}/folder/{folder.slug}/delete/",
        )
        self.assertEqual(
            resolve(f"/user/{user.username}/folder/{folder.slug}/delete/").view_name,
            "pastes:user_folder_delete",
        )

    def test_detail(self):
        user = User.objects.create_user(username="Test")
        paste = Paste.objects.create(
            content="Hello world!",
            author=user,
        )

        self.assertEqual(
            reverse(
                "pastes:detail",
                kwargs={
                    "uuid": paste.uuid,
                },
            ),
            f"/{paste.uuid}/",
        )
        self.assertEqual(
            resolve(f"/{paste.uuid}/").view_name,
            "pastes:detail",
        )

    def test_raw_detail(self):
        user = User.objects.create_user(username="Test")
        paste = Paste.objects.create(
            content="Hello world!",
            author=user,
        )

        self.assertEqual(
            reverse(
                "pastes:raw_detail",
                kwargs={
                    "uuid": paste.uuid,
                },
            ),
            f"/{paste.uuid}/raw/",
        )
        self.assertEqual(
            resolve(f"/{paste.uuid}/raw/").view_name,
            "pastes:raw_detail",
        )

    def test_paste_download(self):
        user = User.objects.create_user(username="Test")
        paste = Paste.objects.create(
            content="Hello world!",
            author=user,
        )

        self.assertEqual(
            reverse(
                "pastes:paste_download",
                kwargs={
                    "uuid": paste.uuid,
                },
            ),
            f"/{paste.uuid}/dl/",
        )
        self.assertEqual(
            resolve(f"/{paste.uuid}/dl/").view_name,
            "pastes:paste_download",
        )

    def test_clone(self):
        user = User.objects.create_user(username="Test")
        paste = Paste.objects.create(
            content="Hello world!",
            author=user,
        )

        self.assertEqual(
            reverse(
                "pastes:clone",
                kwargs={
                    "uuid": paste.uuid,
                },
            ),
            f"/{paste.uuid}/clone/",
        )
        self.assertEqual(
            resolve(f"/{paste.uuid}/clone/").view_name,
            "pastes:clone",
        )

    def test_embed(self):
        user = User.objects.create_user(username="Test")
        paste = Paste.objects.create(
            content="Hello world!",
            author=user,
        )

        self.assertEqual(
            reverse(
                "pastes:embed",
                kwargs={
                    "uuid": paste.uuid,
                },
            ),
            f"/{paste.uuid}/embed/",
        )
        self.assertEqual(
            resolve(f"/{paste.uuid}/embed/").view_name,
            "pastes:embed",
        )

    def test_print(self):
        user = User.objects.create_user(username="Test")
        paste = Paste.objects.create(
            content="Hello world!",
            author=user,
        )

        self.assertEqual(
            reverse(
                "pastes:print",
                kwargs={
                    "uuid": paste.uuid,
                },
            ),
            f"/{paste.uuid}/print/",
        )
        self.assertEqual(
            resolve(f"/{paste.uuid}/print/").view_name,
            "pastes:print",
        )

    def test_report(self):
        user = User.objects.create_user(username="Test")
        paste = Paste.objects.create(
            content="Hello world!",
            author=user,
        )

        self.assertEqual(
            reverse(
                "pastes:report",
                kwargs={
                    "uuid": paste.uuid,
                },
            ),
            f"/{paste.uuid}/report/",
        )
        self.assertEqual(
            resolve(f"/{paste.uuid}/report/").view_name,
            "pastes:report",
        )

    def test_detail_with_password(self):
        user = User.objects.create_user(username="Test")
        paste = Paste.objects.create(
            content="Hello world!",
            author=user,
        )

        self.assertEqual(
            reverse(
                "pastes:detail_with_password",
                kwargs={
                    "uuid": paste.uuid,
                },
            ),
            f"/{paste.uuid}/pass/",
        )
        self.assertEqual(
            resolve(f"/{paste.uuid}/pass/").view_name,
            "pastes:detail_with_password",
        )

    def test_update(self):
        user = User.objects.create_user(username="Test")
        paste = Paste.objects.create(
            content="Hello world!",
            author=user,
        )

        self.assertEqual(
            reverse(
                "pastes:update",
                kwargs={
                    "uuid": paste.uuid,
                },
            ),
            f"/{paste.uuid}/edit/",
        )
        self.assertEqual(
            resolve(f"/{paste.uuid}/edit/").view_name,
            "pastes:update",
        )

    def test_delete(self):
        user = User.objects.create_user(username="Test")
        paste = Paste.objects.create(
            content="Hello world!",
            author=user,
        )

        self.assertEqual(
            reverse(
                "pastes:delete",
                kwargs={
                    "uuid": paste.uuid,
                },
            ),
            f"/{paste.uuid}/delete/",
        )
        self.assertEqual(
            resolve(f"/{paste.uuid}/delete/").view_name,
            "pastes:delete",
        )
