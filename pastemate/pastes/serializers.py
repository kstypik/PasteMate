from rest_framework import serializers

from pastemate.pastes.models import Paste


class PasteSerializer(serializers.HyperlinkedModelSerializer):
    paste_url = serializers.CharField(source="get_absolute_url", read_only=True)

    class Meta:
        model = Paste
        fields = [
            "url",
            "uuid",
            "title",
            "created",
            "filesize",
            "expiration_date",
            "exposure",
            "syntax",
            "hits",
            "paste_url",
        ]
        read_only_fields = [
            "url",
            "uuid",
            "created",
            "filesize",
            "expiration_date",
            "hits",
            "paste_url",
        ]
