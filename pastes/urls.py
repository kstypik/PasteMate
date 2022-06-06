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
    path("<uuid:uuid>/raw/", views.RawPasteDetailView.as_view(), name="raw_detail"),
    path("<uuid:uuid>/dl/", views.DownloadPasteView.as_view(), name="paste_download"),
    path("<uuid:uuid>/clone/", views.PasteCloneView.as_view(), name="clone"),
    path(
        "<uuid:uuid>/pass/",
        views.PasteDetailWithPasswordView.as_view(),
        name="detail_with_password",
    ),
    path("<uuid:uuid>/edit/", views.PasteUpdateView.as_view(), name="update"),
    path("<uuid:uuid>/delete/", views.PasteDeleteView.as_view(), name="delete"),
    path("", views.PasteCreateView.as_view(), name="create"),
]
