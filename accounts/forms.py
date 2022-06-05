from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()


class ProfileForm(forms.ModelForm):
    username = forms.CharField(disabled=True, required=False)

    class Meta:
        model = User
        fields = ["username", "avatar", "location", "website"]
