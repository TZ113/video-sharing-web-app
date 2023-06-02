from celery import shared_task
from django.http import HttpResponseServerError
from moviepy.editor import VideoFileClip

from .utils1 import check_file_path


@shared_task
def convert_video(input_path, output_path):
    """Convert a video from given input to the output path."""

    check_file_path(input_path)
    clip = VideoFileClip(input_path)

    if output_path.endswith(".mp4"):
        # Try to convert to mp4, handle exception
        try:
            clip.write_videofile(
                output_path,
                codec="libx264",
                audio_codec="aac",
            )
        except Exception as e:
            print(
                f"Error occurred:- {e}",
            )
            raise HttpResponseServerError(
                "An error occurred during the video conversion process."
            )
    elif output_path.endswith(".webm"):
        # Try to convert to webm, handle exceptions
        try:
            clip.write_videofile(output_path, codec="libvpx-vp9")
        except Exception as e:
            print(
                f"Error occurred:- {e}",
            )
            raise HttpResponseServerError(
                "An error occurred during the video conversion process."
            )
    else:
        print("Output format can only be 'mp4' and 'webm'.")

    return output_path
