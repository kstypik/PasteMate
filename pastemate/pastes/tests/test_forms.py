from django.contrib.auth import get_user_model
from django.forms import BooleanField
from django.test import TestCase
from hcaptcha_field import hCaptchaField

from .. import forms
from ..models import Folder, Paste

User = get_user_model()


class PasteFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="Test", email="test@test.com", password="test123"
        )
        self.paste = Paste.objects.create(
            content="Hello",
            syntax="html",
            expiration_symbol=Paste.NEVER,
            exposure=Paste.Exposure.PRIVATE,
        )

    def test_form_respects_preferences_of_logged_users(self):
        self.user.preferences.default_syntax = "python"
        self.user.preferences.default_expiration_symbol = "10M"
        self.user.preferences.default_exposure = "PR"
        form = forms.PasteForm(user=self.user, initial={})

        self.assertEqual(form.initial["syntax"], "python")
        self.assertEqual(form.initial["expiration_symbol"], "10M")
        self.assertEqual(form.initial["exposure"], "PR")

    def test_preferences_do_not_override_data_on_update(self):
        self.user.preferences.default_syntax = "python"
        self.user.preferences.default_expiration_symbol = "10M"
        self.user.preferences.default_exposure = "PR"
        form = forms.PasteForm(user=self.user, initial={}, instance=self.paste)

        self.assertEqual(form.initial["syntax"], "html")
        self.assertEqual(form.initial["expiration_symbol"], Paste.NO_CHANGE)
        self.assertEqual(form.initial["exposure"], Paste.Exposure.PRIVATE)

    def test_form_no_change_of_syntax_when_in_initial(self):
        self.user.preferences.default_syntax = "python"
        form = forms.PasteForm(user=self.user, initial={"syntax": "html"})

        self.assertEqual(form.initial["syntax"], "html")

    def test_folder_choices_only_for_folders_created_by_the_user(self):
        another_user = User.objects.create_user(
            username="another", email="another@mail.com"
        )
        folder1 = Folder.objects.create(name="folder1", created_by=self.user)
        folder2 = Folder.objects.create(name="folder2", created_by=self.user)
        folder3 = Folder.objects.create(name="folder3", created_by=another_user)

        form = forms.PasteForm(user=self.user, initial={})

        self.assertIn(folder1, form.fields["folder"].queryset)
        self.assertIn(folder2, form.fields["folder"].queryset)
        self.assertNotIn(folder3, form.fields["folder"].queryset)

    def test_folder_options_only_for_logged_users(self):
        form = forms.PasteForm(initial={})

        self.assertIsNone(form.fields.get("folder"))
        self.assertIsNone(form.fields.get("new_folder"))

    def test_does_not_display_private_exposure_for_unlogged(self):
        form = forms.PasteForm(initial={})

        self.assertNotIn(("PR", "Private"), form.fields["exposure"].choices)

    def test_displays_captcha_only_for_unlogged(self):
        form_for_logged = forms.PasteForm(user=self.user, initial={})
        form_for_unlogged = forms.PasteForm(initial={})

        self.assertIsNone(form_for_logged.fields.get("hcaptcha"))
        self.assertIsInstance(form_for_unlogged.fields["hcaptcha"], hCaptchaField)

    def test_post_anonymously_only_for_logged(self):
        form_for_logged = forms.PasteForm(user=self.user, initial={})
        form_for_unlogged = forms.PasteForm(initial={})

        self.assertIsNone(form_for_unlogged.fields.get("post_anonymously"))
        self.assertIsInstance(form_for_logged.fields["post_anonymously"], BooleanField)

    def test_does_not_display_no_change_expiration_when_no_instance(self):
        form = forms.PasteForm(user=self.user, initial={})

        self.assertNotIn(
            ("PRE", "Don't Change"), form.fields["expiration_symbol"].choices
        )

    def test_form_raises_error_when_paste_set_as_private_and_anonymous(self):
        form = forms.PasteForm(
            user=self.user,
            data={"post_anonymously": True, "exposure": Paste.Exposure.PRIVATE},
            initial={},
        )

        self.assertEqual(
            form.non_field_errors(), ["You can't create private paste as Anonymous."]
        )

    def test_expiration_symbol_is_deleted_when_no_change_chosen(self):
        form = forms.PasteForm(
            user=self.user,
            data={
                "content": "Hello",
                "syntax": "python",
                "expiration_symbol": Paste.NO_CHANGE,
            },
            initial={},
        )

        form.is_valid()

        self.assertIsNone(form.cleaned_data.get("expiration_symbol"))

    def test_folder_is_set_correctly_when_already_exists(self):
        Folder.objects.create(name="test", created_by=self.user)
        form = forms.PasteForm(
            user=self.user,
            data={
                "content": "Hello World",
                "syntax": "python",
                "exposure": Paste.Exposure.PUBLIC,
                "expiration_symbol": Paste.NEVER,
                "new_folder": "test",
            },
            initial={},
        )
        if form.is_valid():
            form.save()
        else:
            self.fail()

        self.assertEqual(Folder.objects.count(), 1)

    def test_folder_is_created_and_set_when_does_not_exist(self):
        form = forms.PasteForm(
            user=self.user,
            data={
                "content": "Hello World",
                "syntax": "python",
                "exposure": Paste.Exposure.PUBLIC,
                "expiration_symbol": Paste.NEVER,
                "new_folder": "new",
            },
            initial={},
        )
        if form.is_valid():
            saved_paste = form.save()
        else:
            self.fail()

        folder = Folder.objects.first()
        self.assertEqual(Folder.objects.count(), 1)
        self.assertEqual(saved_paste.folder.name, folder.name)
        self.assertEqual(saved_paste.folder.created_by, self.user)

    def test_folder_is_ignored_when_posting_anonymously(self):
        form = forms.PasteForm(
            user=self.user,
            data={
                "content": "Hello World",
                "syntax": "python",
                "exposure": Paste.Exposure.PUBLIC,
                "expiration_symbol": Paste.NEVER,
                "new_folder": "should be ignored",
                "post_anonymously": True,
            },
            initial={},
        )
        if form.is_valid():
            saved_paste = form.save()
        else:
            self.fail()

        self.assertEqual(Folder.objects.count(), 0)
        self.assertIsNone(saved_paste.folder)


class PasswordProtectedPasteFormTest(TestCase):
    def test_raises_error_when_password_incorrect(self):
        form = forms.PasswordProtectedPasteForm(
            data={"password": "wrong"}, correct_password="good"
        )

        self.assertEqual(form.errors["password"], ["Password incorrect"])

    def test_validates_when_passwords_match(self):
        form = forms.PasswordProtectedPasteForm(
            data={"password": "good"}, correct_password="good"
        )

        self.assertTrue(form.is_valid())


class FolderFormTest(TestCase):
    def test_raises_error_when_folder_already_exists(self):
        user = User.objects.create_user(username="Test", email="test@test.com")
        Folder.objects.create(name="exists", created_by=user)
        form = forms.FolderForm(user=user, data={"name": "exists"})

        self.assertEqual(
            form.errors["name"], ["You already have a folder with that name"]
        )

    def test_validates_when_folder_does_not_exist(self):
        user = User.objects.create_user(username="Test", email="test@test.com")
        form = forms.FolderForm(user=user, data={"name": "does not exist"})

        self.assertTrue(form.is_valid())
