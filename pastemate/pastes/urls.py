from django.urls import include, path
from rest_framework.routers import SimpleRouter

from pastes import views, views_api

app_name = "pastes"

router = SimpleRouter()
router.register("pastes", views_api.PasteViewSet, basename="pastes")
router.register("folders", views_api.FolderViewSet, basename="folders")


urlpatterns = [
    path("archive/", views.archive, name="archive"),
    path(
        "archive/<str:syntax>/",
        views.archive,
        name="syntax_archive",
    ),
    path("languages/", views.syntax_languages, name="syntax_languages"),
    path("search/", views.search_pastes, name="search"),
    path("backup/", views.backup_pastes, name="backup"),
    path("user/<str:username>/", views.user_pastes, name="user_pastes"),
    path(
        "user/<str:username>/folder/<slug:folder_slug>/",
        views.folder_detail,
        name="user_folder",
    ),
    path(
        "user/<str:username>/folder/<slug:folder_slug>/edit/",
        views.edit_folder,
        name="user_folder_edit",
    ),
    path(
        "user/<str:username>/folder/<slug:folder_slug>/delete/",
        views.delete_folder,
        name="user_folder_delete",
    ),
    path("<uuid:uuid>/", views.paste_detail, name="detail"),
    path("<uuid:uuid>/raw/", views.raw_paste_detail, name="raw_detail"),
    path("<uuid:uuid>/dl/", views.download_paste, name="paste_download"),
    path("<uuid:paste_uuid>/clone/", views.clone_paste, name="clone"),
    path("<uuid:uuid>/embed/", views.embed_paste, name="embed"),
    path("<uuid:uuid>/print/", views.print_paste, name="print"),
    path("<uuid:uuid>/report/", views.report_paste, name="report"),
    path(
        "<uuid:uuid>/pass/",
        views.paste_detail_with_password,
        name="detail_with_password",
    ),
    path("<uuid:uuid>/edit/", views.edit_paste, name="update"),
    path("<uuid:uuid>/delete/", views.delete_paste, name="delete"),
    path("api/", include(router.urls)),
    path("", views.create_paste, name="create"),
]
