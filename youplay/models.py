import os
import uuid

import bleach
from accounts.models import User
from django.core.exceptions import ValidationError
from django.core.files.storage import default_storage as ds
from django.core.validators import (
    FileExtensionValidator,
    MaxLengthValidator,
    MinLengthValidator,
)
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from .utils1 import is_valid_video, time_passed


class Video(models.Model):
    """Model representing videos."""

    title = models.CharField(
        max_length=100,
        validators=[MinLengthValidator(3), MaxLengthValidator(100)],
        help_text=_("Title cannot be longer than 100 characters."),
        error_messages={
            "max_length": _("Title cannot exceed 100 characters"),
            "min_length": _("Title cannot be less than 3 characters."),
        },
    )
    uploader = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="uploaded_videos"
    )
    description = models.TextField(
        max_length=4000,
        blank=True,
        validators=[MaxLengthValidator(4000)],
        help_text=_("4000 characters maximum."),
        error_messages={"max_length": _("Description cannot exceed 4000 characters.")},
    )

    def video_path(instance, filename):
        """Generate a file path for the video."""
        filename = ds.get_valid_name(filename)
        return f"user_{instance.uploader_id}/videos/video_{instance.uuid}/{filename}"

    def thumbnail_path(instance, filename):
        """Generate a file path for the thumbnail."""
        filename = ds.get_valid_name(filename)
        return f"user_{instance.uploader_id}/videos/video_{instance.uuid}/images/thumbnail_{filename}"

    allowed_video_extensions = [
        "mp4",
        "avi",
        "mkv",
        "mov",
        "wmv",
        "webm",
        "ogg",
        "flv",
        "3gp",
        "mkv",
    ]
    video = models.FileField(
        upload_to=video_path,
        validators=[
            FileExtensionValidator(
                allowed_extensions=allowed_video_extensions,
                message=_(
                    "Only these extensions are allowed:- .avi, .mkv, .mov, .wmv, .webm, .ogg, .flv, .3gp, .mkv"
                ),
            ),
        ],
        help_text=_(
            "Allowed extensions are:- .mp4, .avi, .mkv, .mov, .wmv, .webm, .ogg, .flv, .3gp, .mkv"
        ),
    )

    # allowed_thumbnail_extensions_default = ["bmp", "dib", "gif", "tif", "tiff", "jfif", "jpe", "jpg", "jpeg", "pbm", "pgm", "ppm", "pnm", "png", "apng", "blp", "bufr", "cur", "pcx", "dcx", "dds", "ps", "eps", "fit", "fits", "fli", "flc", "fpx", "ftc", "ftu", "gbr", "grib", "h5", "hdf", "jp2", "j2k", "jpc", "jpf", "jpx", "j2c", "icns", "ico", "im", "iim", "mic", "mpg", "mpeg", "mpo", "msp", "palm", "pcd", "pdf", "pxr", "psd", "bw", "rgb", "rgba", "sgi", "ras", "tga", "icb", "vda", "vst", "webp", "wmf", "emf", "xbm", "xpm"]

    allowed_thumbnail_extensions = ["jpg", "jpeg", "png", "svg", "bmp", "gif", "tiff"]
    thumbnail = models.ImageField(
        upload_to=thumbnail_path,
        blank=True,
        validators=[
            FileExtensionValidator(
                allowed_extensions=allowed_thumbnail_extensions,
            )
        ],
        help_text=_("Allowed extensions are:- .jpg, .jpeg, .png, .bmp, .gif, .tiff."),
        error_messages={
            "invalid_extension": _(
                "Only these extensions are allowed:- .jpg, .jpeg, .png, .bmp, .gif, .tiff."
            )
        },
    )

    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    slug = models.SlugField(max_length=255, unique=True, blank=True, editable=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    views = models.IntegerField(default=0)
    processing = models.BooleanField(default=True)
    secondary_video_path = models.CharField(blank=True, max_length=100)

    class Meta:
        ordering = ["title", "timestamp"]
        get_latest_by = ["timestamp"]
        constraints = [  # Add constraints so that an users uploaded videos must have unique titles
            models.UniqueConstraint(fields=["title", "uploader"], name="unique_video")
        ]

    def save(self, *args, **kwargs):
        """modify this method to add some functionalities when a new instance is saved."""

        # Create an uuid and directories for saving uploaded videos and images using it
        if not self.id:
            self.uuid = uuid.uuid4()
            path = f"uploads/user_{self.uploader.id}/videos/video_{self.uuid}/images"
            if not os.path.exists(path):
                try:
                    os.makedirs(path)
                except (PermissionError, OSError) as e:
                    print(e)
                    raise Exception(
                        f"An error occurred while trying to create directories:- {e}"
                    )
        print(f"UUID for video {self.title}:- {self.uuid}")
        # Create a slug from the title and assign it to the slug field
        if not self.slug:
            self.slug = slugify(f"{self.title}-{self.uuid}")
            print(f"Slug for video {self.title}:- {self.slug}")

        super().save()

    def clean(self):
        """Modify this method to perform some additional sanitization and validation."""
        super().clean()

        # Sanitize the title and description fields using the bleach module
        self.title = bleach.clean(self.title, tags=[], attributes=[])
        self.description = bleach.linkify(
            bleach.clean(self.description, tags=[], attributes=[])
        )

        # If a new instance is being created or value of the video field is being changed
        if hasattr(self.video.file, "temporary_file_path"):
            # Validate the video
            path = self.video.file.temporary_file_path()
            if not is_valid_video(path):
                raise ValidationError(
                    _("The uploaded file is not a valid video file."),
                    code="Invalid_video",
                )

    def __str__(self):
        """Return the string representation of an instance."""
        return f"{self.title} by {self.uploader.username}"

    def serialize(self):
        """Return customized and serialized representation of an instance."""
        return {
            "id": self.id,
            "title": self.title,
            "slug": self.slug,
            "uploader": self.uploader.username,
            "thumbnail": self.thumbnail.name,
            "processing": self.processing,
            "views": self.views,
            "timestamp": self.timestamp.strftime("%b %d %Y, %I %M %p"),
            "time_passed_since_added": time_passed(self.timestamp),
        }


class Comment(models.Model):
    """Model representing user's comments on videos."""

    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name="comments")
    commenter = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="comments_on"
    )
    comment = models.TextField(
        max_length=500,
        validators=[MaxLengthValidator(500)],
        help_text=_("your comment cannot be more than 500 characters"),
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    def clean(self):
        """Modify this method to add some additional sanitization."""
        super().clean()
        self.comment = bleach.linkify(
            bleach.clean(self.comment, tags=[], attributes=[])
        )

    def __str__(self):
        return f"{self.comment}   -{self.commenter.username} on {self.video.title}"

    def serialize(self):
        """Inline serializer method for comments"""
        return {
            "comment": self.comment,
            "commenter": self.commenter.username,
            "commenter_id": self.commenter.id,
            "video": self.video.title,
            "timestamp": self.timestamp.strftime("%b %d %Y, %I %M %p"),
        }


class Subscription(models.Model):
    """Model representing user's subscriptions."""

    subscriber = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="subscriptions"
    )
    subscribed_to = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="subscribers"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["subscriber", "subscribed_to"], name="subscribe_once"
            ),
        ]

    def __str__(self):
        return f"{self.subscriber} is subscribed to {self.subscribed_to}."

    def clean(self):
        """Modify this method so that a user cannot self-subscribe"""
        super().clean()
        if self.subscriber == self.subscribed_to:
            raise ValidationError("A user cannot self-subscribe.")


class Like(models.Model):
    """Model representing user's likes on videos."""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="liked_videos", null=True
    )
    video = models.ForeignKey(
        Video, on_delete=models.CASCADE, related_name="likes", null=True
    )

    class Meta:
        ordering = ["video"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "video"],
                name="like_once",
            )
        ]

    def __str__(self):
        return f"{self.user.username} likes {self.video.title}"


class PlayList(models.Model):
    """model representing playlists created by users"""

    name = models.CharField(
        max_length=100,
        validators=[
            MinLengthValidator(1),
        ],
    )
    creator = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="created_playlists"
    )
    videos = models.ManyToManyField(Video, related_name="in_playlists")
    slug = models.SlugField(max_length=255, blank=True, unique=True, editable=False)

    class Meta:
        ordering = ["name", "creator"]
        constraints = [
            models.UniqueConstraint(fields=["name", "creator"], name="unique_playlist")
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super(PlayList, self).save()

    def clean(self):
        super().clean()
        self.name = bleach.clean(self.name, tags=[], attributes=[], strip=True)
        if len(self.name) < 1:
            raise ValidationError("Playlist name must have at least 1 character")

    def __str__(self):
        return f"{self.name} by {self.creator}"
