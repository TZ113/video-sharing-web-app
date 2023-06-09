# Generated by Django 4.1.1 on 2023-04-13 13:06

import django.core.validators
import youplay.models
import youplay.utils
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("youplay", "0026_alter_video_video"),
    ]

    operations = [
        migrations.AlterField(
            model_name="video",
            name="video",
            field=models.FileField(
                help_text="Allowed extensions are:- .mp4, .avi, .mkv, .mov, .wmv, .webm, .ogg, .flv, .3gp, .mkv",
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
                        ],
                        message="Only these extensions are allowed:- .avi, .mkv, .mov, .wmv, .webm, .ogg, .flv, .3gp, .mkv",
                    ),
                    youplay.utils1.is_valid_video,
                ],
            ),
        ),
    ]
