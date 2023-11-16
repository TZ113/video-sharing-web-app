from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from . import views

app_name = "accounts"
urlpatterns = [
    path("register", views.register, name="register"),
    path("activate/<uidb64>/<token>", views.activate, name="activate"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("user_profile", views.edit_user_profile, name="user_profile"),
    path("delete_account", views.delete_account, name="delete_account"),
    path()
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
