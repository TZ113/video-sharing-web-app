"""video_sharing_web_app URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.storage import staticfiles_storage
from django.urls import include, path
from django.views.generic.base import RedirectView

urlpatterns = [
    path("admin/", admin.site.urls),
    path(
        "home/",
        include("youplay.urls"),
    ),
    path(
        "users/",
        include("accounts.urls"),
    ),
    path("accounts/", include("allauth.urls")),
    path(
        "site.webmanifest",
        RedirectView.as_view(url=staticfiles_storage.url("/favicon/site.webmanifest")),
    ),
    path(
        "favicon.ico",
        RedirectView.as_view(url=staticfiles_storage.url("/favicon/favicon.ico")),
    ),
    path(
        "favicon-32x32.png",
        RedirectView.as_view(url=staticfiles_storage.url("/favicon/favicon-32x32.png")),
    ),
    path(
        "favicon-16x16.png",
        RedirectView.as_view(url=staticfiles_storage.url("/favicon/favicon-16x16.png")),
    ),
    path(
        "android-chrome-192x192.png",
        RedirectView.as_view(
            url=staticfiles_storage.url("/favicon/android-chrome-192x192.png")
        ),
    ),
    path(
        "android-chrome-512x512.png",
        RedirectView.as_view(
            url=staticfiles_storage.url("/favicon/android-chrome-512x512.png")
        ),
    ),
    path(
        "apple-touch-icon.png",
        RedirectView.as_view(
            url=staticfiles_storage.url("/favicon/apple-touch-icon.png")
        ),
    ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
