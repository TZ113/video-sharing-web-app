# Generated by Django 4.1.9 on 2023-05-27 07:03

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("youplay", "0032_alter_playlist_slug"),
    ]

    operations = [
        migrations.CreateModel(
            name="ConvertedFilenames",
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
                ("filename", models.CharField(max_length=100)),
            ],
        ),
    ]
