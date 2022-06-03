from django.urls import path

from . import views

app_name = "pastes"

urlpatterns = [
    path("", views.PasteCreateView.as_view(), name="create"),
]
