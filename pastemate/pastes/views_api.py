from rest_framework import renderers, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from pastes.models import Paste
from pastes.serializers import FolderSerializer, PasteSerializer


class PasteViewSet(viewsets.ModelViewSet):
    queryset = Paste.objects.all()
    serializer_class = PasteSerializer

    def get_queryset(self):
        return self.request.user.paste_set.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, renderer_classes=[renderers.StaticHTMLRenderer])
    def raw(self, request, *args, **kwargs):
        return Response(self.get_object().content)


class FolderViewSet(viewsets.ModelViewSet):
    serializer_class = FolderSerializer

    def get_queryset(self):
        return self.request.user.folders.all()

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
