import os
import random

from django.core.files.storage import default_storage as ds
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from PIL import Image

from .models import Video
from .tasks import convert_video
from .utils import get_output_paths, take_random_snapshots


# @receiver(pre_delete, sender=Video)
def delete_files_and_directories(sender, instance, *args, **kwargs):
    """Delete video and image files, and directories when a video is being deleted."""

    # Get the paths
    base_path = os.path.split(instance.video.name)[0]
    primary_video_path = instance.video.name
    secondary_video_path = instance.secondary_video_path

    # Delete the primary video
    if primary_video_path != "" and ds.exists(primary_video_path):
        ds.delete(primary_video_path)
    else:
        print("The video file path doesn't exist!")

    # Delete the backup video
    if secondary_video_path != "" and ds.exists(secondary_video_path):
        ds.delete(secondary_video_path)
    else:
        print("The secondary video file path doesn't exist!")

    # get the image files path and names
    images_path = os.path.split(instance.thumbnail.name)[0]
    image_file_names = ds.listdir(images_path)[1]

    # Delete each of the image files
    for name in image_file_names:
        ds.delete(f"{images_path}/{name}")

    # Try to delete the images path, handle exceptions
    # Any exceptions that might've occurred during deleting the image files will be caught here
    try:
        ds.delete(images_path)
    except (PermissionError, OSError) as e:
        raise Exception(f"An error occurred while trying to delete image files:- {e}")

    # Do the same with the base path of the video
    try:
        ds.delete(base_path)
    except (PermissionError, OSError) as e:
        raise Exception(
            f"An error occurred while trying to delete files and directories for this video:- {e}"
        )

    print("video files and directories deleted")


@receiver(post_save, sender=Video)
def process_video(created, instance, *args, **kwargs):
    """Further process an instance and update the database. Each uploaded video is converted to one mp4 and one webm format, and if the file is already in one of those format than converted only to the other. The mp4 is then stored as the primary video file, and the webm as a backup. Several snapshots are taken from the video. If the user hasn't uploaded a thumbnail, one of the snapshots is used for that. Finally, the database is updated based on the changes done."""

    # Only the first time the instance is saved
    if created:
        # For using with the `default_storage` or `ds` the, `MEDIA_ROOT`, which is the 'uploads' directory needs to be excluded,
        # But for other cases it needs to be included as the starting directory of the path

        if instance.video and ds.exists(instance.video.name):
            input_path = f"uploads/{instance.video.name}"

            output_paths = get_output_paths(input_path)
            converted_file_names = []
            for path in output_paths:
                # Trigger the celery task for converting the video and get the result
                res = convert_video.delay(input_path, path)
                path_name = res.get()
                # Store the results
                converted_file_names.append("/".join(path_name.split("/")[1:]))

            filename, ext = os.path.splitext(
                instance.video.name
            )  # Name and extension of the originally uploaded video file
            file_path = os.path.split(filename)[
                0
            ]  # The directory of the video file, which now contains the converted files as well

            if ext not in [".mp4", ".webm"]:
                # Uploaded video is neither mp4 or webm
                mp4_name = [
                    name for name in converted_file_names if name.endswith("mp4")
                ][0]
                webm_name = [
                    name for name in converted_file_names if name.endswith("webm")
                ][0]

                # Try to remove the originally uploaded file, handle exceptions
                try:
                    os.remove(input_path)
                except (OSError, PermissionError) as e:
                    raise Exception(
                        f"An error occurred while trying to remove file:- {e}."
                    )

                # Set the necessary field values
                instance.video.name = mp4_name
                instance.secondary_video_path = webm_name

            else:
                if ext == ".mp4":
                    # Uploaded file is mp4
                    instance.secondary_video_path = converted_file_names[0]
                else:
                    print("Uploaded file is webm")
                    instance.secondary_video_path = instance.video.name
                    instance.video.name = converted_file_names[0]

            # Update the modified fields
            instance.save(update_fields=["video", "secondary_video_path"])

            # Take 5 random snapshots from the video and save them to the video's 'images' directory
            video_file_path = f"uploads/{instance.video.name}"
            print(f"Path passed to snap:- {video_file_path}")
            snaps = take_random_snapshots(video_file_path, 5)
            for i in range(len(snaps)):
                img = Image.fromarray(snaps[i])
                img.save(
                    f"uploads/user_{instance.uploader_id}/videos/video_{instance.uuid}/images/snap_{i + 1}.jpg"
                )

        # If the user uploaded a thumbnail, resize and save the image
        if instance.thumbnail and ds.exists(instance.thumbnail.name):
            image_path = f"uploads/{instance.thumbnail.name}"
            img = Image.open(image_path)
            if img.size != (300, 200):
                img = img.resize((300, 200))
                img = img.convert("RGB")
                img.save(image_path)
        # Else assign one of the snapshots as thumbnail for the video
        else:
            path_to_snaps = f"uploads/user_{instance.uploader_id}/videos/video_{instance.uuid}/images"
            snap_names = os.listdir(path_to_snaps)

            # Select a random snap
            selected_snap = random.choice(snap_names)
            img = Image.open(f"{path_to_snaps}/{selected_snap}")

            # Resize if necessary
            if img.size != (300, 200):
                img = img.resize((300, 200))

            # Save the image in the thumbnail path
            thumbnail_path = f"{file_path}/images/thumbnail_{selected_snap}"
            img.save(f"uploads/{thumbnail_path}")

            # Update the thumbnail field of the video
            instance.thumbnail.name = thumbnail_path
            instance.save(
                update_fields=[
                    "thumbnail",
                ]
            )

        # Update the processing field
        instance.processing = False
        instance.save(update_fields=["processing"])
