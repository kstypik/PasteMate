from django.urls import path

from . import views

app_name = "pastes"

urlpatterns = [
    path("<uuid:uuid>/", views.PasteDetailView.as_view(), name="detail"),
    path("<uuid:uuid>/edit/", views.PasteUpdateView.as_view(), name="update"),
    path("<uuid:uuid>/delete/", views.PasteDeleteView.as_view(), name="delete"),
    path("", views.PasteCreateView.as_view(), name="create"),
]
