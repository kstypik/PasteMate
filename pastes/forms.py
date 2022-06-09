from django import forms

from .models import Folder, Paste, Report


class PasteForm(forms.ModelForm):
    new_folder = forms.CharField(
        max_length=50,
        required=False,
        help_text="You can type a new folder name, and it will be created and chosen instead of the one above.",
    )
    post_anonymously = forms.BooleanField(
        help_text="If checked, your account won't be associated with this paste. You won't be able to edit or delete it later.",
        required=False,
    )

    class Meta:
        model = Paste
        fields = [
            "content",
            "syntax",
            "exposure",
            "expiration_time",
            "folder",
            "new_folder",
            "password",
            "burn_after_read",
            "title",
        ]

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        self.fields["folder"].queryset = Folder.objects.filter(created_by=self.user)
        if not self.user:
            del self.fields["folder"]
            del self.fields["new_folder"]
        if kwargs.get("instance") or not self.user:
            del self.fields["post_anonymously"]

    def clean(self):
        cleaned_data = super().clean()
        if (
            cleaned_data.get("post_anonymously")
            and cleaned_data.get("exposure") == "PR"
        ):
            raise forms.ValidationError("You can't create private paste as Anonymous.")

    def save(self, commit=True):
        paste = super().save(commit=False)
        new_folder = self.cleaned_data["new_folder"]
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
        if password != self.correct_password:
            raise forms.ValidationError("Password incorrect")


class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ["reason", "reporter_name"]
