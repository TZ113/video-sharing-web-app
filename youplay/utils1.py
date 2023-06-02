import os
import subprocess

from django.utils import timezone


def check_file_path(path):
    """Check if a file exist in the given path, raise `Http404` otherwise."""
    if not os.path.isfile(path):
        raise OSError(f"{path} doesn't exist in the filesystem.")


def time_passed(timestamp):
    """Generate a more human readable representation of the time passed since the creation of a video."""
    # Check if the passed timestamp is valid
    try:
        timezone.datetime.fromtimestamp(timestamp.timestamp())
    except ValueError:
        raise ValueError(f"{timestamp} isn't a valid timestamp.")

    time_elapsed = timezone.now() - timestamp
    seconds_elapsed = time_elapsed.total_seconds()

    # Return more human readable string
    if seconds_elapsed < 60:
        return f"{round(seconds_elapsed)} seconds"
    elif seconds_elapsed < (60 * 60):
        return f"{round( seconds_elapsed / 60)} mins"
    elif seconds_elapsed < (60 * 60 * 24):
        return f"{round(seconds_elapsed / (60 * 60))} hours"
    elif seconds_elapsed < (60 * 60 * 24 * 7):
        return f"{round(seconds_elapsed / (60 * 60 *24))} days"
    elif seconds_elapsed < (60 * 60 * 24 * 7 * 4.345):
        return f"{round(seconds_elapsed / (60 * 60 * 24 * 7))} weeks"
    elif seconds_elapsed < (60 * 60 * 24 * 7 * 4.345 * 12):
        return f"{round(seconds_elapsed / (60 * 60 * 24 * 7 * 4.345))} months"
    elif seconds_elapsed < (60 * 60 * 24 * 7 * 4.345 * 12 * 100):
        return f"{round(seconds_elapsed / (60 * 60 * 24 * 7 * 4.345 * 12))} years"
    elif seconds_elapsed < (60 * 60 * 24 * 7 * 4.345 * 12 * 100 * 10):
        return f"{round(seconds_elapsed / (60 * 60 * 24 * 7 * 4.345 * 12 * 100))} centuries"
    elif seconds_elapsed < (60 * 60 * 24 * 7 * 4.345 * 12 * 100 * 10 * 100):
        return f"{round(seconds_elapsed / (60 * 60 * 24 * 7 * 4.345 * 12 * 100 * 10))} millennia"
    else:
        return "a really really long time"


def is_valid_video(file_path):
    """Check if a video is valid or not."""

    # Check if the file path is valid
    check_file_path(file_path)

    # Define the ffprobe command to check the video codec and container format
    command = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=format_name",
        "-select_streams",
        "v:0",
        "-show_entries",
        "stream=codec_name",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        file_path,
    ]

    # Run the ffprobe command and capture the output
    result = subprocess.run(command, check=False, capture_output=True)

    # If the command fails to execute, return False
    if result.returncode != 0:
        print(f"Command failed with status code {result.returncode}")
        return False

    # Get the codec and container from the result
    output = result.stdout.decode("utf-8").strip().split("\n")

    # If either of the codec or the container is absent in the output return False
    if len(output) < 2:
        print("Either codec or container not found.")
        return False

    # Define valid codecs and container formats
    valid_codecs = [
        "h264",
        "h265",
        "vp8",
        "vp9",
        "av1",
        "mpeg4",
        "mpeg2",
        "wmv2",
        "wmv3",
        "vc1",
        "h263",
        "theora",
        "flv1",
    ]
    valid_containers = [
        "mp4",
        "avi",
        "mkv",
        "mov",
        "wmv",
        "webm",
        "ogg",
        "flv",
        "3gp",
        "m4a",
        "3g2",
        "mj2",
        "matroska",
        "asf",
    ]

    # Check if the codec and container format is in the lists of valid codecs and containers
    codec_valid = output[0].lower() in valid_codecs
    container_valid = all(
        container in valid_containers for container in output[1].lower().split(",")
    )

    return codec_valid and container_valid
