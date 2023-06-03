# Generated by Django 4.1.1 on 2023-03-12 12:56

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import youplay.models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("youplay", "0013_remove_watchlater_user_remove_watchlater_videos_and_more"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="like",
            options={"ordering": ["video"]},
        ),
        migrations.AlterModelOptions(
            name="playlist",
            options={"ordering": ["name", "creator"]},
        ),
        migrations.AlterUniqueTogether(
            name="like",
            unique_together=set(),
        ),
        migrations.AlterUniqueTogether(
            name="playlist",
            unique_together=set(),
        ),
        migrations.AlterField(
            model_name="comment",
            name="commenter",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="comments_on",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name="comment",
            name="video",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="comments",
                to="youplay.video",
            ),
        ),
        migrations.AlterField(
            model_name="like",
            name="user",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="liked_videos",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name="like",
            name="video",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="likes",
                to="youplay.video",
            ),
        ),
        migrations.AlterField(
            model_name="video",
            name="description",
            field=models.TextField(
                blank=True, help_text="4000 characters maximum.", max_length=4000
            ),
        ),
        migrations.AlterField(
            model_name="video",
            name="thumbnail",
            field=models.ImageField(
                blank=True,
                help_text="Only these extensions are allowed:- .jpg, .jpeg, .bmp, .gif, .tiff.",
                upload_to=youplay.models.Video.thumbnail_path,
                validators=[
                    django.core.validators.FileExtensionValidator(
                        allowed_extensions=["jpg", "jpeg", "png", "bmp", "gif", "tiff"],
                        message="Only these extensions are allowed:- .jpg, .jpeg, .bmp, .gif, .tiff.",
                    )
                ],
            ),
        ),
        migrations.AlterField(
            model_name="video",
            name="uploader",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="uploaded_videos",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name="video",
            name="video",
            field=models.FileField(
                help_text="Only these extensions are allowed:- .mp4, .avi, .mkv, .mov, .wmv, .webm, .ogg, .flv, .3gp, .mkv, .m4a.",
                upload_to=youplay.models.Video.video_path,
                validators=[
                    django.core.validators.FileExtensionValidator(
                        allowed_extensions=[
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
                            "m4a",
                        ],
                        message="Only these extensions are allowed:- .mp4, .avi, .mkv, .mov, .wmv, .webm, .ogg, .flv, .3gp, .mkv, .m4a.",
                    )
                ],
            ),
        ),
        migrations.AddConstraint(
            model_name="like",
            constraint=models.UniqueConstraint(
                fields=("user", "video"), name="like_once"
            ),
        ),
        migrations.AddConstraint(
            model_name="playlist",
            constraint=models.UniqueConstraint(
                fields=("name", "creator"), name="unique_playlist"
            ),
        ),
    ]