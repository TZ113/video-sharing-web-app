# Generated by Django 4.1.1 on 2023-04-12 15:23

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("youplay", "0024_alter_video_uploader"),
    ]

    operations = [
        migrations.AlterField(
            model_name="video",
            name="uploader",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="uploaded_videos",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
