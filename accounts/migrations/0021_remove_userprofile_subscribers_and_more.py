# Generated by Django 4.1.1 on 2023-04-04 17:41

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0020_alter_user_managers"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="userprofile",
            name="subscribers",
        ),
        migrations.RemoveField(
            model_name="userprofile",
            name="subscriptions",
        ),
    ]
