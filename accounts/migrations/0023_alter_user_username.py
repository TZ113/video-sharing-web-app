# Generated by Django 4.1.1 on 2023-04-20 15:11

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0022_alter_user_email_alter_user_username_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="username",
            field=models.CharField(
                error_messages={
                    "max_length": "Username cannot exceed 100 characters.",
                    "min_length": "username needs to be at least 5 characters long.",
                    "unique": "An user with that name already exists.",
                },
                help_text="Username needs to be between 3 and 30 characters. Besides letters and numbers, only _, -, . and @ are allowed  ",
                max_length=30,
                unique=True,
                validators=[
                    django.core.validators.MinLengthValidator(3),
                    django.core.validators.MaxLengthValidator(30),
                    django.core.validators.RegexValidator(
                        "^[a-zA-Z0-9_-.@]+$",
                        "Besides letters and numbers only _, -, . and @ are allowed, no spaces too.",
                    ),
                ],
                verbose_name="username",
            ),
        ),
    ]