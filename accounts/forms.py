from django import forms
from django.contrib.auth import authenticate, get_user_model

User = get_user_model()


class ProfileForm(forms.ModelForm):
    username = forms.CharField(disabled=True, required=False)

    class Meta:
        model = User
        fields = ["username", "avatar", "location", "website"]


class AccountDeleteForm(forms.Form):
    password = forms.CharField(
        widget=forms.PasswordInput,
        label="Your current password",
        help_text="Enter your current password to confirm deletion",
    )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super().__init__(*args, **kwargs)

    def clean_password(self):
        input_password = self.cleaned_data.get("password")
        if not authenticate(
            self.request, username=self.request.user.username, password=input_password
        ):
            raise forms.ValidationError("Entered password is invalid.")
