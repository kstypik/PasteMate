from django import forms
from django.contrib.auth.hashers import check_password
from hcaptcha_field import hCaptchaField

from pastes.models import Folder, Paste, Report

NEW_FOLDER_HELP_TEXT = "You can type a new folder name, and it will be created and chosen instead of the one above."
POST_ANONYMOUSLY_HELP_TEXT = (
    "If checked, your account won't be associated with this paste.\
                             You won't be able to edit or delete it later."
)


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
    title = forms.CharField(initial="Untitled", required=False)
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
        self.passed_instance = kwargs.get("instance")
        super().__init__(*args, **kwargs)

        self.remove_folder_options_for_guest()

        self.handle_user_preferences()
        self.handle_expiration()
        self.handle_password(data=kwargs.get("data"))
        self.set_user_folder_choices()

        if self.user:
            del self.fields["hcaptcha"]

        if self.passed_instance or not self.user:
            del self.fields["post_anonymously"]

    def remove_folder_options_for_guest(self):
        if not self.user:
            del self.fields["folder"]
            del self.fields["new_folder"]

    def handle_user_preferences(self):
        if self.user and not self.passed_instance:
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

    def handle_expiration(self):
        if self.passed_instance:
            self.initial.update({"expiration_symbol": "PRE"})
        else:
            self.fields["expiration_symbol"].choices = filter(
                lambda option: option[0] != Paste.NO_CHANGE,
                self.fields["expiration_symbol"].choices,
            )

    def handle_password(self, data):
        if self.passed_instance and data:
            if data.get("enablePassword") and not data.get("password"):
                del self.fields["password"]
            else:
                self.instance.password = ""

    def set_user_folder_choices(self):
        if self.user:
            self.fields["folder"].queryset = self.user.folders.all()

    def clean(self):
        cleaned_data = super().clean()
        if (cleaned_data.get("post_anonymously") or not self.user) and cleaned_data.get(
            "exposure"
        ) == Paste.Exposure.PRIVATE:
            msg = "You can't create private paste as Anonymous."
            raise forms.ValidationError(msg)

        return cleaned_data

    def save(self, commit=True):  # noqa: FBT002
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
            msg = "Password incorrect"
            raise forms.ValidationError(msg)
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
            msg = "You already have a folder with that name"
            raise forms.ValidationError(msg)

        return self.cleaned_data["name"]
