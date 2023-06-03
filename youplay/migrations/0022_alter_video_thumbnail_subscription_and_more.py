# Generated by Django 4.1.1 on 2023-04-04 17:41

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import youplay.models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("youplay", "0021_alter_comment_comment_alter_playlist_name"),
    ]

    operations = [
        migrations.AlterField(
            model_name="video",
            name="thumbnail",
            field=models.ImageField(
                blank=True,
                error_messages={
                    "invalid_extension": "Only these extensions are allowed:- .jpg, .jpeg, .png, .bmp, .gif, .tiff."
                },
                help_text="Allowed extensions are:- .jpg, .jpeg, .png, .bmp, .gif, .tiff.",
                upload_to=youplay.models.Video.thumbnail_path,
                validators=[
                    django.core.validators.FileExtensionValidator(
                        allowed_extensions=[
                            "jpg",
                            "jpeg",
                            "png",
                            "svg",
                            "bmp",
                            "gif",
                            "tiff",
                        ]
                    )
                ],
            ),
        ),
        migrations.CreateModel(
            name="Subscription",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "subscribed_to",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="subscribers",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "subscriber",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="subscriptions",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.AddConstraint(
            model_name="subscription",
            constraint=models.UniqueConstraint(
                fields=("subscriber", "subscribed_to"), name="subscribe_once"
            ),
        ),
    ]