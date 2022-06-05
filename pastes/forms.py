from django import forms

from .models import Folder, Paste


class PasteForm(forms.ModelForm):
    new_folder = forms.CharField(
        max_length=50,
        required=False,
        help_text="You can type a new folder name, and it will be created and chosen instead of the one above.",
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
        if not self.user:
            del self.fields["folder"]
            del self.fields["new_folder"]

    def save(self, commit=True):
        paste = super().save(commit=False)
        if self.user:
            new_folder = self.cleaned_data["new_folder"]
            folder, _ = Folder.objects.get_or_create(
                created_by=self.user, name=new_folder
            )
            paste.folder = folder
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
