# Generated by Django 4.1.1 on 2022-12-26 14:43

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('youplay', '0010_subscription_unique_subscription'),
        ('accounts', '0008_userprofile_about_userprofile_subscribers_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='subscribers',
            field=models.ManyToManyField(blank=True, related_name='subscriber', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='subscriptions',
            field=models.ManyToManyField(blank=True, related_name='subscribed_tos', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='watchlater',
            field=models.ManyToManyField(blank=True, to='youplay.video'),
        ),
    ]
