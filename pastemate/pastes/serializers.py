from rest_framework import serializers

from pastemate.pastes.models import Paste


class PasteSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="pastes:pastes-detail")

    class Meta:
        model = Paste
        fields = [
            "content",
            "title",
            "syntax",
            "created",
            "filesize",
            "expiration_date",
            "expiration_symbol",
            "exposure",
            "password",
            "burn_after_read",
            "url",
        ]
        read_only_fields = [
            "created",
            "filesize",
            "expiration_date",
        ]
        extra_kwargs = {
            "content": {"write_only": True},
            "expiration_symbol": {"write_only": True},
            "password": {"write_only": True},
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["expiration_symbol"].choices = filter(
            lambda option: option not in (Paste.NO_CHANGE, Paste.NEVER),
            self.fields["expiration_symbol"].choices,
        )
