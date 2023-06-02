# Generated by Django 4.1.1 on 2023-04-29 13:25

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0024_alter_user_username"),
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
                        "^[\\w\\.\\-@]+[\\w\\s\\.\\-@]*$",
                        "Besides letters and numbers only _, -, ., @ and spaces are allowed.",
                    ),
                ],
                verbose_name="username",
            ),
        ),
    ]
