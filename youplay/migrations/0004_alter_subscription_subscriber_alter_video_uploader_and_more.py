# Generated by Django 4.1.1 on 2022-11-28 13:50

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import youplay.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('youplay', '0003_alter_comment_timestamp_alter_video_description_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subscription',
            name='subscriber',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subscribed_to', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='video',
            name='uploader',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='uploaded', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='video',
            name='video',
            field=models.FileField(help_text='Only these extensions are allowed:- .mp4, .avi, .mkv, .mov, .wmv, .webm, .ogg, .flv, .3gp, .mkv, .m4a', upload_to=youplay.models.Video.video_path, validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['mp4', 'avi', 'mkv', 'mov', 'wmv', 'webm', 'ogg', 'flv', '3gp', 'mkv', 'm4a'], message='Only these extensions are allowed:- .mp4, .avi, .mkv, .mov, .wmv, .webm, .ogg, .flv, .3gp, .mkv, .m4a')]),
        ),
    ]