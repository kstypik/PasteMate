from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from knox import views as knox_views

from accounts import views_api

urlpatterns = [
    path(settings.ADMIN_URL, admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("accounts/", include("allauth.urls")),
    path("", include("pastes.urls")),
    path("api/auth/login/", views_api.LoginView.as_view(), name="knox_login"),
    path("api/auth/logout/", knox_views.LogoutView.as_view(), name="knox_logout"),
    path(
        "api/auth/logoutall/", knox_views.LogoutAllView.as_view(), name="knox_logoutall"
    ),
    path("api/user/", views_api.UserProfileView.as_view(), name="api_profile"),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/schema/swagger-ui/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "api/schema/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
    *static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT),
]

if settings.DEBUG:
    urlpatterns += (path("__debug__/", include("debug_toolbar.urls")),)
