# Generated by Django 4.1.1 on 2022-12-27 18:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('youplay', '0010_subscription_unique_subscription'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='video',
            options={'get_latest_by': ['-timestamp'], 'ordering': ['title', '-timestamp']},
        ),
        migrations.AlterUniqueTogether(
            name='video',
            unique_together=set(),
        ),
        migrations.AddConstraint(
            model_name='video',
            constraint=models.UniqueConstraint(fields=('title', 'uploader'), name='unique_video'),
        ),
    ]
