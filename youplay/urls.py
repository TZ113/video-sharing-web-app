from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from . import views

app_name = "youplay"

urlpatterns = [
    path("", views.index, name="index"),
    path("upload", views.upload, name="upload"),
    path("video/<slug:slug>", views.video, name="video"),
    path("update_video/<int:video_id>", views.update_video, name="update_video"),
    path("delete_video/<int:video_id>", views.delete_video, name="delete_video"),
    path("play_video/<slug:slug>", views.play_video, name="play_video"),
    path("search", views.search, name="search"),
    path("comments", views.add_or_get_comments, name="comments"),
    path("processing_status", views.processing_status, name="processing_status"),
    path("profiles/<int:user_id>", views.profile, name="profile"),
    path(
        "subscribe_unsubscribe",
        views.subscribe_unsubscribe,
        name="subscribe_unsubscribe",
    ),
    path("get_playlists", views.get_playlists, name="get_playlists"),
    path(
        "update_playlists",
        views.update_playlists,
        name="update_playlists",
    ),
    path("list_videos/<str:list_name>", views.list_videos, name="list_videos"),
    path(
        "delete_playlist/<str:playlist_name>",
        views.delete_playlist,
        name="delete_playlist",
    ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
