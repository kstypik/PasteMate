from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("edit-profile/", views.ProfileUpdateView.as_view(), name="profile_update"),
]
