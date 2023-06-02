import os

from django.core.files.storage import default_storage as ds
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from PIL import Image, ImageDraw, ImageFont

from .models import User, UserProfile


def create_directories(instance_id):
    """Create necessary directories for storing user's files."""
    base_path = f"user_{instance_id}"
    videos_path = f"{base_path}/videos"
    profile_pictures_path = f"{base_path}/profile_pictures"
    if instance_id and not ds.exists(base_path):
        # Try to create the directories, handle exceptions
        try:
            os.makedirs(f"uploads/{videos_path}")
            os.makedirs(f"uploads/{profile_pictures_path}")
        except (PermissionError, OSError) as e:
            raise Exception(
                f"An error occurred while trying to create storage for the user:- {e}."
            )

    print(f"directories created for user {instance_id}")


def create_default_profile_picture(letter):
    """Create an image from the letter."""
    img = Image.new("RGB", (180, 180), (0, 102, 255))
    canvas = ImageDraw.Draw(img)
    font = ImageFont.truetype("accounts/static/accounts/Backslash-RpJol.otf", 130)
    canvas.text((90, 97), letter.upper(), fill="white", font=font, anchor="mm")

    return img


@receiver(pre_delete, sender=User)
def delete_files_and_directories(sender, instance, **kwargs):
    """Delete the file upload directories along with all the uploaded videos and thumbnails of the user instance. This will only be called if the admin is deleting an user instance permanently."""
    base_path = f"user_{instance.id}"
    videos_path = f"{base_path}/videos"
    profile_pictures_path = f"{base_path}/profile_pictures"

    # Delete the profile pictures
    profile_picture_names = ds.listdir(profile_pictures_path)[1]
    for name in profile_picture_names:
        ds.delete(f"{profile_pictures_path}/{name}")

    # Delete the profile_pictures directory
    ds.delete(profile_pictures_path)

    all_video_dirs = ds.listdir(videos_path)[0]  # Each directories containing videos
    for dir in all_video_dirs:
        video_names = ds.listdir(dir)[1]

        # Delete the video files in the directory
        for name in video_names:
            ds.delete(f"{videos_path}/{dir}/{name}")

        images_path = f"{videos_path}/{dir}/images"
        image_names = ds.listdir(images_path)[1]

        # Delete each image files
        for name in image_names:
            ds.delete(f"{images_path}/{name}")

        # Delete the directory containing image files, then the parent which contained the video files
        ds.delete(images_path)
        ds.delete(f"{videos_path}/{dir}")

    # Delete the videos directory
    ds.delete(videos_path)

    # Try to delete the base directory, handle exceptions
    # If anything went wrong while deleting the directories and files inside
    # Will be caught in this block
    try:
        ds.delete(base_path)
    except (PermissionError, OSError) as e:
        raise Exception(
            f"An error occurred while trying to delete files and directories of user {instance.id}:- {e}"
        )

    print("files and directories deleted")


@receiver(post_save, sender=User)
def create_directories_and_update_database(created, sender, instance, *args, **kwargs):
    """Create directories for storing the user's uploads. Also create a default profile picture."""

    # Only when the instance is created
    if created:
        print(f"new user {instance.id} is created")

        # Create necessary directories
        create_directories(instance.id)

        # Create default profile picture from the first letter of username
        image = create_default_profile_picture(instance.username[0])

        path = f"user_{instance.id}/profile_pictures/profile_pic_default.jpg"

        # Try to save the image, handle exceptions
        try:
            image.save(f"uploads/{path}")
        except (PermissionError, OSError) as e:
            raise Exception(
                f"An error occurred while trying to create profile picture:- {e}"
            )

        # Create an userProfile instance for the current user and adds the default profile picture to it
        UserProfile.objects.create(user=instance, profile_picture=path)
