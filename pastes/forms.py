from django import forms

from .models import Paste


class PasteForm(forms.ModelForm):
    class Meta:
        model = Paste
        fields = [
            "content",
            "syntax",
            "exposure",
            "expiration_time",
            "password",
            "burn_after_read",
            "title",
        ]


class PasswordProtectedPasteForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        self.correct_password = kwargs.pop("correct_password")
        super().__init__(*args, **kwargs)

    def clean_password(self):
        password = self.cleaned_data["password"]
        if password != self.correct_password:
            raise forms.ValidationError("Password incorrect")
