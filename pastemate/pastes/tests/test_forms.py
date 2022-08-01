import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.forms import BooleanField
from hcaptcha_field import hCaptchaField

from pastemate.pastes import forms
from pastemate.pastes.models import Folder, Paste

pytestmark = pytest.mark.django_db

User = get_user_model()


class TestPasteForm:
    def test_form_respects_preferences_of_logged_users(self, user):
        user.preferences.default_syntax = "python"
        user.preferences.default_expiration_symbol = "10M"
        user.preferences.default_exposure = "PR"
        form = forms.PasteForm(user=user, initial={})

        assert form.initial["syntax"] == "python"
        assert form.initial["expiration_symbol"] == "10M"
        assert form.initial["exposure"] == "PR"

    def test_preferences_do_not_override_data_on_update(self, user, create_paste):
        paste = create_paste(
            author=user, syntax="html", exposure=Paste.Exposure.PRIVATE
        )
        user.preferences.default_syntax = "python"
        user.preferences.default_expiration_symbol = "10M"
        user.preferences.default_exposure = "PR"
        form = forms.PasteForm(user=user, initial={}, instance=paste)

        assert form.initial["syntax"] == "html"
        assert form.initial["expiration_symbol"] == Paste.NO_CHANGE
        assert form.initial["exposure"] == Paste.Exposure.PRIVATE

    def test_form_no_change_of_syntax_when_in_initial(self, user):
        user.preferences.default_syntax = "python"
        form = forms.PasteForm(user=user, initial={"syntax": "html"})

        assert form.initial["syntax"] == "html"

    def test_folder_choices_only_for_folders_created_by_the_user(self, user):
        another_user = User.objects.create_user(
            username="another", email="another@mail.com"
        )
        folder1 = Folder.objects.create(name="folder1", created_by=user)
        folder2 = Folder.objects.create(name="folder2", created_by=user)
        folder3 = Folder.objects.create(name="folder3", created_by=another_user)

        form = forms.PasteForm(user=user, initial={})

        assert folder1 in form.fields["folder"].queryset
        assert folder2 in form.fields["folder"].queryset
        assert folder3 not in form.fields["folder"].queryset

    def test_folder_options_only_for_logged_users(self):
        form = forms.PasteForm(initial={})

        assert form.fields.get("folder") is None
        assert form.fields.get("new_folder") is None

    def test_displays_captcha_only_for_unlogged(self, user):
        form_for_logged = forms.PasteForm(user=user, initial={})
        form_for_unlogged = forms.PasteForm(initial={})

        assert form_for_logged.fields.get("hcaptcha") is None
        assert isinstance(form_for_unlogged.fields["hcaptcha"], hCaptchaField)

    def test_post_anonymously_only_for_logged(self, user):
        form_for_logged = forms.PasteForm(user=user, initial={})
        form_for_unlogged = forms.PasteForm(initial={})

        assert form_for_unlogged.fields.get("post_anonymously") is None
        assert isinstance(form_for_logged.fields["post_anonymously"], BooleanField)

    def test_does_not_display_no_change_expiration_when_no_instance(self, user):
        form = forms.PasteForm(user=user, initial={})

        assert ("PRE", "Don't Change") not in form.fields["expiration_symbol"].choices

    def test_form_raises_error_when_paste_set_as_private_and_anonymous(self, user):
        form = forms.PasteForm(
            user=user,
            data={"post_anonymously": True, "exposure": Paste.Exposure.PRIVATE},
            initial={},
        )

        assert form.non_field_errors() == [
            "You can't create private paste as Anonymous."
        ]

    def test_form_raises_error_when_paste_set_as_private_and_no_user(self, user):
        form = forms.PasteForm(
            data={"post_anonymously": True, "exposure": Paste.Exposure.PRIVATE},
            initial={},
        )

        assert form.non_field_errors() == [
            "You can't create private paste as Anonymous."
        ]

    def test_expiration_symbol_is_deleted_when_no_change_chosen(self, user):
        form = forms.PasteForm(
            user=user,
            data={
                "content": "Hello",
                "syntax": "python",
                "expiration_symbol": Paste.NO_CHANGE,
            },
            initial={},
        )

        form.is_valid()

        assert form.cleaned_data.get("expiration_symbol") is None

    def test_folder_is_set_correctly_when_already_exists(self, user):
        Folder.objects.create(name="test", created_by=user)
        form = forms.PasteForm(
            user=user,
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
            pytest.fail()

        assert Folder.objects.count() == 1

    def test_folder_is_created_and_set_when_does_not_exist(self, user):
        form = forms.PasteForm(
            user=user,
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
            pytest.fail()

        folder = Folder.objects.first()
        assert Folder.objects.count() == 1
        assert saved_paste.folder.name == folder.name
        assert saved_paste.folder.created_by == user

    def test_folder_is_ignored_when_posting_anonymously(self, user):
        form = forms.PasteForm(
            user=user,
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
            pytest.fail()

        assert Folder.objects.count() == 0
        assert saved_paste.folder is None


class TestPasswordProtectedPasteForm:
    def test_raises_error_when_password_incorrect(self):
        form = forms.PasswordProtectedPasteForm(
            data={"password": "wrong"}, correct_password="good"
        )

        assert form.errors["password"] == ["Password incorrect"]

    def test_validates_when_passwords_match(self):
        correct_password = make_password("good")
        form = forms.PasswordProtectedPasteForm(
            data={"password": "good"}, correct_password=correct_password
        )

        assert form.is_valid()


class TestFolderForm:
    def test_raises_error_when_folder_already_exists(self, folder):
        form = forms.FolderForm(user=folder.created_by, data={"name": "Testing folder"})

        assert form.errors["name"] == ["You already have a folder with that name"]

    def test_validates_when_folder_does_not_exist(self, user):
        form = forms.FolderForm(user=user, data={"name": "does not exist"})

        assert form.is_valid()
