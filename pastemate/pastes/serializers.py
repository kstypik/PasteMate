from rest_framework import serializers

from pastemate.pastes.models import Paste


class PasteSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="pastes:pastes-detail")

    class Meta:
        model = Paste
        fields = [
            "title",
            "created",
            "filesize",
            "expiration_date",
            "exposure",
            "syntax",
            "url",
        ]
        read_only_fields = [
            "created",
            "filesize",
            "expiration_date",
        ]
