import bleach
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.core.exceptions import ValidationError
from django.core.files.storage import default_storage as ds
from django.core.mail import send_mail
from django.core.validators import (
    EmailValidator,
    FileExtensionValidator,
    MaxLengthValidator,
    MinLengthValidator,
    RegexValidator,
)
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from PIL import Image

# Create your models here.
email_validator = EmailValidator(message="Enter a valid email address")
username_validator = RegexValidator(
    r"^[\w\.\-@]+[\w\s\.\-@]*$",
    _("Besides letters and numbers only _, -, ., @ and spaces are allowed."),
)


class UserManager(BaseUserManager):
    """Implements certain restrictions while creating a new user."""

    def create_user(self, username, email, password=None, **extra_fields):
        """modify the create_user function so that it only accepts users with an username at least 3 characters long, a valid email and a 8 character long password"""
        if not username or len(username) < 3 or len(username) > 30:
            raise ValueError(
                _("User must have an username with at least 3 characters.")
            )
        try:
            username_validator(username)
        except ValidationError:
            raise ValueError(
                _("Besides letters and numbers only _, -, ., @ and spaces are allowed.")
            )
        if not email:
            raise ValueError(_("User must have an email address."))
        try:
            email_validator(email)
        except ValidationError:
            raise ValueError(_("User must enter a valid email address."))
        self.normalize_email(email)
        if not password or len(password) < 8:
            raise ValueError(
                _("User must have a password that is at least 8 characters long")
            )

        user = self.model(username=username, email=email, **extra_fields)
        print(user)
        user.set_password(password)
        user.save(using=self.db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(username, email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """Model representing users."""

    username = models.CharField(
        _("username"),
        validators=[
            MinLengthValidator(3),
            MaxLengthValidator(30),
            username_validator,
        ],
        max_length=30,
        unique=True,
        help_text=_(
            "Username needs to be between 3 and 30 characters. Besides letters and numbers, only _, -, ., @ and spaces are allowed."
        ),
        error_messages={
            "unique": _("An user with that name already exists."),
            "min_length": _("username needs to be at least 5 characters long."),
            "max_length": _("Username cannot exceed 100 characters."),
        },
    )
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    email = models.EmailField(
        unique=True,
        validators=[email_validator],
        error_messages={"unique": _("An user with that email already exists.")},
    )

    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active. It's recommended that this should be unselected instead deleting the user."
        ),
    )
    is_staff = models.BooleanField(
        _("staff_status"),
        default=False,
        help_text=_("Designates whether this user can log into this admin site."),
    )
    is_superuser = models.BooleanField(
        _("Superuser_status"),
        default=False,
        help_text=_("Designates whether this user is a superuser."),
    )
    date_joined = models.DateTimeField(_("date_joined"), default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = "username"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = ["email"]

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")
        get_latest_by = ["date_joined"]

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def get_short_name(self):
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        send_mail(subject, message, from_email, [self.email], **kwargs)

    def __str__(self):
        """Generate the string representation of an instance."""
        return f"{self.username} with {self.email}"


class UserProfile(models.Model):
    """Model representing additional user data that are essential for the application but not relevant for authentication. Instances are created through post_save signal."""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")

    def profile_pic_path(instance, filename):
        """Generates a file path for the users profile picture."""
        filename = ds.get_valid_name(filename)
        return f"uploads/user_{instance.user_id}/profile_pictures/{filename}"

    allowed_extensions = {"jpeg", "jpg", "bitmap", "png", "gif", "tiff"}
    profile_picture = models.ImageField(
        upload_to=profile_pic_path,
        blank=True,
        validators=[
            FileExtensionValidator(
                allowed_extensions=allowed_extensions,
                message=_(
                    "Only these extensions are allowed:- .jpeg, .jpg, .bitmap, .png, .gif, .tiff"
                ),
            )
        ],
    )
    about = models.TextField(
        max_length=4000,
        blank=True,
        help_text=_("4000 characters maximum."),
        validators=[MaxLengthValidator(4000)],
    )
    watchlater = models.ManyToManyField("youplay.Video", blank=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Save the profile picture in a variable
        self.original_image = self.profile_picture

    def __str__(self):
        return f"{self.user.username}'s profile"

    def clean(self):
        """Modify this method to sanitize the about field using the bleach module."""
        super().clean()
        self.about = bleach.linkify(bleach.clean(self.about, tags=[], attributes=[]))

    def save(self, *args, **kwargs):
        """Modify the save method so that it can handle later profile picture upload by the user."""
        super(UserProfile, self).save(*args, **kwargs)

        # Check if the user has uploaded a profile picture and then modify and save it
        if self.profile_picture != "" and self.original_image != self.profile_picture:
            pic = Image.open(self.profile_picture)
            if pic.size != (180, 180):
                pic = pic.resize((180, 180))
                pic = pic.convert("RGB")
            try:
                pic.save(f"uploads/{self.profile_picture}")
            except (PermissionError, OSError) as e:
                raise Exception(f"An error occurred while trying to save image:- {e}")
