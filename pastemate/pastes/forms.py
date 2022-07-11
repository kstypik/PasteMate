from django import forms
from django.contrib.auth.hashers import check_password
from hcaptcha_field import hCaptchaField

from pastemate.pastes.models import Folder, Paste, Report

NEW_FOLDER_HELP_TEXT = "You can type a new folder name, and it will be created and chosen instead of the one above."
POST_ANONYMOUSLY_HELP_TEXT = "If checked, your account won't be associated with this paste.\
                             You won't be able to edit or delete it later."


class PasteForm(forms.ModelForm):
    content = forms.CharField(widget=forms.Textarea, label="")
    new_folder = forms.CharField(
        max_length=50,
        required=False,
        help_text=NEW_FOLDER_HELP_TEXT,
    )
    post_anonymously = forms.BooleanField(
        help_text=POST_ANONYMOUSLY_HELP_TEXT,
        required=False,
    )
    hcaptcha = hCaptchaField(label="CAPTCHA")

    class Meta:
        model = Paste
        fields = [
            "content",
            "syntax",
            "exposure",
            "expiration_symbol",
            "folder",
            "new_folder",
            "password",
            "burn_after_read",
            "title",
            "post_anonymously",
            "hcaptcha",
        ]

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        passed_instance = kwargs.get("instance")
        super().__init__(*args, **kwargs)

        if self.user and not passed_instance:
            self.initial.update(
                {
                    "exposure": self.user.preferences.default_exposure,
                    "expiration_symbol": self.user.preferences.default_expiration_symbol,
                }
            )
            # Don't override syntax when update/clone
            if not self.initial.get("syntax"):
                self.initial.update(
                    {
                        "syntax": self.user.preferences.default_syntax,
                    }
                )

        if passed_instance:
            self.initial.update({"expiration_symbol": "PRE"})

            if kwargs.get("data"):
                if kwargs["data"].get("enablePassword") and not kwargs["data"].get(
                    "password"
                ):
                    del self.fields["password"]
                else:
                    self.instance.password = ""
        else:
            self.fields["expiration_symbol"].choices = filter(
                lambda option: option[0] != Paste.NO_CHANGE,
                self.fields["expiration_symbol"].choices,
            )

        if self.user:
            self.fields["folder"].queryset = self.user.folders.all()

            del self.fields["hcaptcha"]
        else:
            del self.fields["folder"]
            del self.fields["new_folder"]

            self.fields["exposure"].choices = filter(
                lambda option: option[0] != Paste.Exposure.PRIVATE,
                self.fields["exposure"].choices,
            )

        if passed_instance or not self.user:
            del self.fields["post_anonymously"]

    def clean(self):
        cleaned_data = super().clean()
        if (
            cleaned_data.get("post_anonymously")
            and cleaned_data.get("exposure") == Paste.Exposure.PRIVATE
        ):
            raise forms.ValidationError("You can't create private paste as Anonymous.")

        return cleaned_data

    def save(self, commit=True):
        paste = super().save(commit=False)

        new_folder = self.cleaned_data.get("new_folder")
        post_anonymously = self.cleaned_data.get("post_anonymously")

        if not post_anonymously and self.user and new_folder:
            folder, _ = Folder.objects.get_or_create(
                created_by=self.user, name=new_folder
            )
            paste.folder = folder
        if post_anonymously:
            paste.folder = None

        if commit:
            paste.save()
        return paste


class PasswordProtectedPasteForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        self.correct_password = kwargs.pop("correct_password")
        super().__init__(*args, **kwargs)

    def clean_password(self):
        password = self.cleaned_data["password"]
        if not check_password(password, encoded=self.correct_password):
            raise forms.ValidationError("Password incorrect")
        return password


class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ["reason", "reporter_name"]


class FolderForm(forms.ModelForm):
    class Meta:
        model = Folder
        fields = ["name"]

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")
        super().__init__(*args, **kwargs)

    def clean_name(self):
        if self.user.folders.filter(name__iexact=self.cleaned_data["name"]).exists():
            raise forms.ValidationError("You already have a folder with that name")

        return self.cleaned_data["name"]
