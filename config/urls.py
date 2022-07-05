from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path(settings.ADMIN_URL, admin.site.urls),
    path("accounts/", include("pastemate.accounts.urls")),
    path("accounts/", include("allauth.urls")),
    path("messages/", include("pinax.messages.urls", namespace="pinax_messages")),
    path("", include("pastemate.pastes.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += (path("__debug__/", include("debug_toolbar.urls")),)
