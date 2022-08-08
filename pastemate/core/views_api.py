from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse


@api_view(["GET"])
def api_root(request, format=None):
    return Response(
        {
            "pastes": reverse("pastes:pastes-list", request=request, format=format),
            "user": reverse("api_profile", request=request, format=format),
        }
    )
