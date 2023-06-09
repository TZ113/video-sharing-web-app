# Generated by Django 4.1.1 on 2023-03-14 06:50

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0017_alter_user_managers"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="is_superuser",
            field=models.BooleanField(
                default=False,
                help_text="Designates whether this user is a superuser.",
                verbose_name="Superuser_status",
            ),
        ),
    ]
