from rest_framework import serializers

from pastes.models import Folder, Paste


class PasteSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="pastes:pastes-detail")
    folder = serializers.HyperlinkedRelatedField(
        view_name="pastes:folders-detail", read_only=True
    )

    class Meta:
        model = Paste
        fields = [
            "uuid",
            "content",
            "title",
            "syntax",
            "created",
            "filesize",
            "expiration_date",
            "expiration_symbol",
            "exposure",
            "password",
            "folder",
            "burn_after_read",
            "url",
        ]
        read_only_fields = [
            "uuid",
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


class FolderSerializer(serializers.ModelSerializer):
    pastes = PasteSerializer(many=True, read_only=True)

    class Meta:
        model = Folder
        fields = ["slug", "name", "pastes"]
