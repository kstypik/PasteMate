from django.urls import path

from . import views

app_name = "pastes"

urlpatterns = [
    path("archive/", views.PasteArchiveListView.as_view(), name="archive"),
    path(
        "archive/<str:syntax>/",
        views.PasteArchiveListView.as_view(),
        name="syntax_archive",
    ),
    path("user/<str:username>/", views.UserPasteListView.as_view(), name="user_pastes"),
    path("<uuid:uuid>/", views.PasteDetailView.as_view(), name="detail"),
    path("<uuid:uuid>/edit/", views.PasteUpdateView.as_view(), name="update"),
    path("<uuid:uuid>/delete/", views.PasteDeleteView.as_view(), name="delete"),
    path("", views.PasteCreateView.as_view(), name="create"),
]
