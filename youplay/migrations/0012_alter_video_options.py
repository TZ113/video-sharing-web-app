# Generated by Django 4.1.1 on 2022-12-27 18:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('youplay', '0011_alter_video_options_alter_video_unique_together_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='video',
            options={'get_latest_by': ['timestamp'], 'ordering': ['title', 'timestamp']},
        ),
    ]
