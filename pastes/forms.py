from django import forms
from pygments import lexers

from .models import Paste

SYNTAX_HIGHLITHING_CHOICES = [("", "None")] + [
    (lexer[0], lexer[0]) for lexer in lexers.get_all_lexers()
]


class PasteForm(forms.ModelForm):
    syntax = forms.ChoiceField(choices=SYNTAX_HIGHLITHING_CHOICES, required=False)

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
