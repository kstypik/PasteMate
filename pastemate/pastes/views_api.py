from rest_framework import viewsets

from pastemate.pastes.models import Paste
from pastemate.pastes.serializers import PasteSerializer


class PasteViewSet(viewsets.ModelViewSet):
    queryset = Paste.objects.all()
    serializer_class = PasteSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
