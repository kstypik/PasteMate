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
