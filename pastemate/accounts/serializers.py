from rest_framework import serializers

from accounts.models import Preferences, User


class PreferencesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Preferences
        fields = [
            "default_syntax",
            "default_expiration_symbol",
            "default_exposure",
            "layout_width",
            "paste_font_size",
        ]


class UserSerializer(serializers.ModelSerializer):
    preferences = PreferencesSerializer()

    class Meta:
        model = User
        fields = ["username", "email", "avatar", "website", "location", "preferences"]
