from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from knox import views as knox_views

from pastemate.accounts import views_api
from pastemate.core.views_api import api_root

urlpatterns = [
    path(settings.ADMIN_URL, admin.site.urls),
    path("accounts/", include("pastemate.accounts.urls")),
    path("accounts/", include("allauth.urls")),
    path("messages/", include("pinax.messages.urls", namespace="pinax_messages")),
    path("", include("pastemate.pastes.urls")),
    path("api/auth/login/", views_api.LoginView.as_view(), name="knox_login"),
    path("api/auth/logout/", knox_views.LogoutView.as_view(), name="knox_logout"),
    path(
        "api/auth/logoutall/", knox_views.LogoutAllView.as_view(), name="knox_logoutall"
    ),
    path("api/user/", views_api.UserProfileView.as_view(), name="api_profile"),
    path("api/", api_root, name="api_root"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += (path("__debug__/", include("debug_toolbar.urls")),)
