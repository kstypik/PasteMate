from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from pastemate.accounts import views_api

urlpatterns = [
    path(settings.ADMIN_URL, admin.site.urls),
    path("accounts/", include("pastemate.accounts.urls")),
    path("accounts/", include("allauth.urls")),
    path("messages/", include("pinax.messages.urls", namespace="pinax_messages")),
    path("", include("pastemate.pastes.urls")),
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
    path("api/user/", views_api.UserProfileView.as_view(), name="api_profile"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += (path("__debug__/", include("debug_toolbar.urls")),)
