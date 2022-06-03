from django.urls import path

from . import views

app_name = "pastes"

urlpatterns = [
    path("<uuid:uuid>/", views.PasteDetailView.as_view(), name="detail"),
    path("", views.PasteCreateView.as_view(), name="create"),
]
