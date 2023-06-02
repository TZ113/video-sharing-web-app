# Generated by Django 4.1.1 on 2023-05-03 07:52

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):
    dependencies = [
        ("youplay", "0030_video_slug"),
    ]

    operations = [
        migrations.AddField(
            model_name="playlist",
            name="slug",
            field=models.SlugField(
                blank=True, editable=False, max_length=255, null=True, unique=True
            ),
        ),
        migrations.AlterField(
            model_name="video",
            name="slug",
            field=models.SlugField(
                blank=True,
                default=django.utils.timezone.now,
                editable=False,
                max_length=255,
                unique=True,
            ),
            preserve_default=False,
        ),
    ]
