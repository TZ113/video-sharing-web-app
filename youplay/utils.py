import os
import random

from django.core.files.storage import default_storage as ds
from moviepy.editor import VideoFileClip

from .utils1 import check_file_path


def check_num(num):
    """Check if an integer is valid or can be converted to, raise `ValueError` otherwise."""
    if not isinstance(num, int):
        try:
            num = int(num)
        except ValueError:
            raise ValueError(f"'{num}' needs to be an integer.")
    return num


def make_more_readable(num):
    """Generate a more human readable format of the given number (of views, likes etc)."""

    # Check the given number
    num = check_num(num)

    # Return more human readable string format
    if num >= 100000000:
        return f"{round(num / 1000000000, 1)}B"
    elif num >= 1000000:
        return f"{round(num / 1000000, 1)}M"
    elif num >= 1000:
        return f"{round(num / 1000, 1)}K"
    else:
        return str(num)


def take_random_snapshots(video_file_path, num_snaps):
    """Take the given number of snapshots from the video with the given file path using moviepy module."""

    # Check if the arguments are valid
    check_file_path(video_file_path)
    num_snaps = check_num(num_snaps)

    clip = VideoFileClip(video_file_path)
    duration = clip.duration
    snaps = []
    for i in range(num_snaps):
        # get a random time within the video duration
        t = random.uniform(0, duration)
        # get the frame at the random time
        frame = clip.get_frame(t)
        # add the frame to the list of snapshots
        snaps.append(frame)

    return snaps


def get_output_paths(input_path):
    """generate and return output paths from the given input path."""

    check_file_path(input_path)
    filename, ext = os.path.splitext(input_path)
    output_paths = []

    # Construct the output paths
    path_mp4 = ds.get_available_name(filename + ".mp4")
    path_webm = ds.get_available_name(filename + ".webm")

    # Append the path or paths to the list
    if ext.lower() == ".mp4":
        output_paths.append(path_webm)
    elif ext.lower() == ".webm":
        output_paths.append(path_mp4)
    else:
        output_paths.append(path_mp4)
        output_paths.append(path_webm)

    # return the list
    return output_paths
