from rest_framework import serializers

from pastemate.pastes.models import Paste


class PasteSerializer(serializers.ModelSerializer):
    paste_url = serializers.CharField(source="get_absolute_url", read_only=True)

    class Meta:
        model = Paste
        fields = [
            "uuid",
            "title",
            "created",
            "filesize",
            "expiration_date",
            "exposure",
            "syntax",
            "paste_url",
        ]
        read_only_fields = [
            "uuid",
            "created",
            "filesize",
            "expiration_date",
            "paste_url",
        ]
