# Generated by Django 4.1.1 on 2023-04-21 06:57

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):
    dependencies = [
        ("youplay", "0028_alter_video_video"),
    ]

    operations = [
        migrations.AddField(
            model_name="video",
            name="uuid",
            field=models.UUIDField(default=uuid.uuid4, editable=False),
        ),
    ]