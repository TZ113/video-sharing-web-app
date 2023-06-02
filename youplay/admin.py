from django.contrib import admin

from .models import Comment, Like, PlayList, Subscription, Video


# Register your models here.
class VideoAdmin(admin.ModelAdmin):
    list_display = ("__str__",)
    search_fields = ("id", "title", "uploader__username")


class CommentAdmin(admin.ModelAdmin):
    list_display = ("__str__",)
    search_fields = ("id", "video__title", "commenter__username")


class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("__str__",)
    search_fields = ("id", "subscriber_username", "subscribed_to_username")


class LikeAdmin(admin.ModelAdmin):
    list_display = ("__str__",)


class PlayListAdmin(admin.ModelAdmin):
    list_display = ("__str__",)
    filter_horizontal = ("videos",)
    search_fields = ("id", "name", "creator__username", "videos__title")


# Registering in the admin panel
admin.site.register(Video, VideoAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
admin.site.register(Like, LikeAdmin)
admin.site.register(PlayList, PlayListAdmin)
