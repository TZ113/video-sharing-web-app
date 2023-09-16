import json
import time
from collections import defaultdict
from itertools import chain

from accounts.models import User, UserProfile
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.db.models import F, Q
from django.db.transaction import TransactionManagementError
from django.http import Http404, HttpResponseNotAllowed, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from ranged_response import RangedFileResponse

from .forms import EditDescriptionForm, UploadForm
from .models import Comment, Like, PlayList, Subscription, Video
from .utils import make_more_readable


# Create your views here.
def get_data_segment(start, end, items):
    """Return a list containing a specific number of elements, from start to end, from the querySet items."""

    if len(items) == 0 or len(items) < start:
        return

    if items.model == Video:
        for video in items:
            video.views = make_more_readable(video.views)

    # Create an empty list and appends the specified number of elements to it
    data = []
    if len(items) <= end:
        [data.append(items[i]) for i in range(start, len(items))]
    else:
        [data.append(items[i]) for i in range(start, end + 1)]

    time.sleep(1)

    # Return the elements list
    return data


def get_video(video_id):
    """Return the video object with the specified id, raise an 'Http404' in case of exceptions."""
    try:
        video = Video.objects.get(pk=video_id)
    except Video.DoesNotExist:
        raise Http404("Requested video does not exist.")
    except (TypeError, ValueError):
        raise Http404("The video id needs to be a number.")

    return video


def updateLike(request, video):
    """Create or delete an instance of model class 'Like'."""

    like = Like.objects.filter(user=request.user, video=video)
    status = ""

    # If the instance exists, that means the user is giving an unlike
    if like.exists():
        status = "unlike"

        try:
            like.delete()
        except Exception as e:
            raise Exception(
                f"An error occurred while trying to perform database operation:- {e}"
            )

    # The user is giving a like
    else:
        status = "like"

        try:
            new_like = Like(user=request.user, video=video)
            new_like.full_clean()
            new_like.save()

        except IntegrityError as e:
            if "UNIQUE constraint failed:" in str(e):
                return JsonResponse(
                    {"error": "You cannot like a video twice."}, status=400
                )
        except Exception as e:
            raise Exception(
                f"An error occurred while trying to perform database operation:- {e}"
            )

    return status


def updateViews(video_id):
    """Increment the views field by 1 for the video with given id."""

    try:
        Video.objects.filter(pk=video_id).update(views=F("views") + 1)
    except Exception as e:
        raise Exception(f"An error occurred while trying to update database:- {e}")


def updateVideoDescription(form):
    """Update the description field of the 'Video' with the given model form."""
    if form.is_valid():
        form.save()
        return True
    else:
        return False


def index(request):
    """Render the Homepage."""
    if request.GET.get("start") and request.GET.get("end"):
        # Get the videos from start to end from a querySet of all videos and return it
        start = int(request.GET.get("start"))
        end = int(request.GET.get("end"))

        videos = Video.objects.all().order_by("-timestamp")

        # Get the specific range of videos from the querySet
        data = get_data_segment(start, end, videos)

        # If any videos exist within that range, Serialize and return them with a status code 200, else return a status code 204
        if data is not None:
            return JsonResponse(
                {"all": [video.serialize() for video in data]}, status=200
            )
        else:
            return JsonResponse({}, status=204)

    if request.GET.get("message"):
        # If there are any messages, render the page with it
        message = request.GET.get("message")
        return render(request, "youplay/index.html", {"message": message})

    return render(request, "youplay/index.html")


@login_required
def upload(request):
    """Handle video upload by the user."""

    if request.method == "POST":
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            # Try to save form with the user as uploader, handle exception
            try:
                video = form.save(commit=False)
                video.uploader = request.user
                video.save()
            # Most exceptions are handled in the models and forms validation processes
            except Exception as e:
                raise Exception(
                    f"An error occurred while trying to save video to the database:- {e}"
                )

            return JsonResponse({"video_id": video.id}, status=201)

        # If the form is invalid, Collect the error messages in a dict, return that as a JsonResponse
        else:
            error_messages = {}
            if form.errors:
                for field in form.fields:
                    if form.errors.get(field):
                        error_messages[field] = [
                            error.messages for error in form.errors.as_data()[field]
                        ]
                if form.errors.get("__all__"):
                    error_messages["all"] = [
                        error.messages for error in form.errors.as_data()["__all__"]
                    ]

            return JsonResponse({"error_messages": error_messages}, status=400)

    return render(request, "youplay/upload.html", {"uploadForm": UploadForm()})


def video(request, slug):
    """Display the video page."""

    video = get_object_or_404(Video, slug=slug)

    total_likes = make_more_readable(video.likes.count())
    readable_views = make_more_readable(video.views)

    current_user_likes = (
        True
        if request.user.is_authenticated
        and Like.objects.filter(user=request.user, video=video)
        else False
    )

    current_user_subscribed = (
        True
        if request.user.is_authenticated
        and Subscription.objects.filter(
            subscriber=request.user, subscribed_to=video.uploader
        ).exists()
        else False
    )

    return render(
        request,
        "youplay/video.html",
        {
            "video_data": video,
            "description_form": EditDescriptionForm(instance=video),
            "total_likes": total_likes,
            "views": readable_views,
            "current_user_likes": current_user_likes,
            "current_user_subscribed": current_user_subscribed,
        },
    )


@login_required
def update_video(request, video_id):
    """Handle users update of like, view and video description."""
    video = get_video(video_id)

    if request.method == "PUT":
        # Update the designated model or field

        data = json.loads(request.body)
        if data["updating"] == "like":
            status = updateLike(request, video)
            total_likes = make_more_readable(Like.objects.filter(video=video).count())

            return JsonResponse({"status": status, "likes": total_likes})

        elif data["updating"] == "view":
            updateViews(video.id)
            video.refresh_from_db(fields=["views"])
            views = make_more_readable(video.views)
            return JsonResponse({"views": views})

    elif request.method == "POST" and "description" in request.POST.keys():
        description_form = EditDescriptionForm(request.POST, instance=video)
        if updateVideoDescription(description_form):
            return redirect("youplay:video", slug=video.slug)
        else:
            return render(
                request,
                "youplay/video.html",
                {
                    "video_data": video,
                    "description_form": description_form,
                    "error": True,
                },
            )
    else:
        return HttpResponseNotAllowed(["PUT", "POST"])


def processing_status(request):
    """Return if a video is currently being processed or not."""

    if request.GET.get("id"):
        while True:
            video = get_object_or_404(Video, pk=request.GET.get("id"))
            if video.processing == False:
                return JsonResponse(
                    {"processing": False, "thumbnail_path": video.thumbnail.name}
                )


def play_video(request, slug):
    """Retrieve a video from the database and return it as ranged response."""

    video = get_object_or_404(Video, slug=slug)

    filename = f"{settings.MEDIA_ROOT}/{video.video.name}"
    backup_filename = f"{settings.MEDIA_ROOT}/{video.secondary_video_path}"

    # Try to stream the video
    try:
        response = RangedFileResponse(
            request, open(filename, "rb"), content_type="video/mp4"
        )
        response["Content-Disposition"] = f"inline; filename={filename}"
    except FileNotFoundError:
        print("Primary video file isn't available.")
        try:
            response = RangedFileResponse(
                request, open(backup_filename, "rb"), content_type="video/mp4"
            )
            response["Content-Disposition"] = f"inline; filename={backup_filename}"
        except FileNotFoundError:
            raise Http404("The requested video doesn't exist.")

    return response


def add_or_get_comments(request):
    """Add users comments on videos to database or return a specific number of instances to the pages requesting them."""

    if request.method == "POST":
        data = json.loads(request.body)
        comment = data["comment"]
        video = get_video(data["video_id"])

        if comment:
            # Try to add the comment to the database, handle exceptions
            try:
                new_comment = Comment(
                    commenter=request.user, video=video, comment=comment
                )
                new_comment.full_clean()
                new_comment.save()
            except ValidationError as e:
                return JsonResponse({"error": e.messages}, status=400)

            except Exception as e:
                raise Exception(
                    f"An error occurred while trying to perform database operation:- {e}"
                )

            return JsonResponse(
                {"comment": new_comment.serialize()}, safe=False, status=201
            )
        else:
            print("no comment!")

    if (
        request.GET.get("start")
        and request.GET.get("end")
        and request.GET.get("video_id")
    ):
        # Get the comments ranging from start to end and return with status code 200,
        # If none exists return status code 204
        start = int(request.GET.get("start"))
        end = int(request.GET.get("end"))
        comments = Comment.objects.filter(
            video=Video.objects.get(pk=request.GET.get("video_id"))
        ).order_by("-timestamp")

        data = get_data_segment(start, end, comments)

        time.sleep(1)
        if data is not None:
            return JsonResponse(
                [comment.serialize() for comment in data], safe=False, status=200
            )
        else:
            return JsonResponse({}, status=204)


def profile(request, user_id):
    """Render the profile page of users except the current user."""
    user = get_object_or_404(User, pk=user_id)

    if request.GET.get("start") and request.GET.get("end"):
        start = int(request.GET.get("start"))
        end = int(request.GET.get("end"))
        videos = Video.objects.filter(uploader=request.user).order_by("-timestamp")
        data = get_data_segment(start, end, videos)
        if data is not None:
            return JsonResponse(
                {"profile": [video.serialize() for video in data]}, status=200
            )
        else:
            return JsonResponse({}, status=204)

    current_user_subscribed = (
        True
        if request.user.is_authenticated
        and Subscription.objects.filter(
            subscriber=request.user, subscribed_to=user
        ).exists()
        else False
    )

    total_subscribers = Subscription.objects.filter(subscribed_to=user).count()

    return render(
        request,
        "youplay/profile.html",
        {
            "user_data": user,
            "current_user_subscribed": current_user_subscribed,
            "total_subscribers": total_subscribers,
        },
    )


@login_required
def subscribe_unsubscribe(request):
    """Handle subscriptions."""
    if request.method == "PUT":
        data = json.loads(request.body)
        user = get_object_or_404(User, pk=data["user_id"])

        subscription = Subscription.objects.filter(
            subscriber=request.user, subscribed_to=user
        )
        status = ""

        # If the subscription already exists, that means the user is trying to unsubscribe
        if subscription.exists():
            try:
                subscription.delete()
            except Exception as e:
                raise Exception(
                    f"An error occurred while trying to perform database operation:- {e}"
                )
            status = "unsubscribed"

        # The user is trying to subscribe
        else:
            try:
                new_subscription = Subscription(
                    subscriber=request.user, subscribed_to=user
                )
                new_subscription.full_clean()
                new_subscription.save()
            except IntegrityError as e:
                if "UNIQUE constraint failed:" in str(e):
                    return JsonResponse({"error": e.messages}, status=400)
            except ValidationError as e:
                return JsonResponse({"error": e.messages}, status=400)
            except Exception as e:
                raise Exception(
                    f"Error occurred while trying to perform database operation:- {e}"
                )
            status = "subscribed"

        subscribers = make_more_readable(
            Subscription.objects.filter(subscribed_to=user).count()
        )
        return JsonResponse({"subscribers": subscribers, "status": status})
    else:
        return HttpResponseNotAllowed(["PUT"])


def search(request):
    """Handle user's search requests for videos."""

    query = request.GET.get("q").strip()

    # Get the necessary field values for all the exactly matching videos
    exact_matches = (
        Video.objects.filter(Q(title__exact=query) | Q(title__iexact=query))
        .order_by("-views")
        .values_list("id", "title", "uploader__username", "views")
    )

    # And sort the querySet by number of views, and then the relative length of the titles
    exact_matches = sorted(
        exact_matches, key=lambda i: (i[3], 100 - len(i[1])), reverse=True
    )

    # All the other videos to check
    videos_to_check = Video.objects.exclude(
        pk__in=[i[0] for i in exact_matches]
    ).values_list("id", "title")

    word_counter = defaultdict(int)
    character_counter = defaultdict(int)

    # For each video to be checked, check if the title contains the query or the other way around,
    # both case sensitively and insensitively, and if match happens
    # set the video id as a key in word_counter dict, increment its value by 1
    for video in videos_to_check:
        title = video[1].strip()
        if query in title:
            word_counter[video[0]] = 1
        if query.lower() in title.lower():
            word_counter[video[0]] += 1
        if title in query:
            word_counter[video[0]] = 1
        if title.lower() in query.lower():
            word_counter[video[0]] += 1

    words_in_query = query.split()

    for word in words_in_query:
        # Filter the videos containing word
        videos_containing_word = videos_to_check.filter(title__contains=word)
        if videos_containing_word.exists():
            for video in videos_containing_word:
                # With the video id as key, increase the word_counter by the number of counts of the word in the title
                word_counter[video[0]] += video[1].count(word)

        # Repeat the process case insensitively
        videos_containing_word_i = videos_to_check.filter(title__icontains=word)
        if videos_containing_word_i.exists():
            for video in videos_containing_word_i:
                word_counter[video[0]] += video[1].count(word)

    # Get the remaining videos and check for character matching
    videos_not_matched_by_word = videos_to_check.exclude(pk__in=word_counter.keys())
    if videos_not_matched_by_word.exists():
        for character in "".join(query.split()):
            videos_containing_character = videos_not_matched_by_word.filter(
                title__contains=character
            )
            if videos_containing_character.exists():
                # Set the video id as a key in the character_counter dict, and number of count in title as value
                for video in videos_containing_character:
                    character_counter[video[0]] = video[1].count(character)

            # Repeat the process case insensitively, update the dict
            videos_containing_character_i = videos_not_matched_by_word.filter(
                title__icontains=character
            )
            if videos_containing_character_i.exists():
                for video in videos_containing_character_i:
                    character_counter[video[0]] += (
                        video[1].lower().count(character.lower())
                    )

    # Get the necessary field values for all the videos whose title matched words of the query
    videos_matched_by_words = Video.objects.filter(
        pk__in=word_counter.keys()
    ).values_list("id", "title", "uploader__username", "views")

    # Sort the querySet by number of count in word_counter, number of views and then the relative length of the title
    videos_matched_by_words = sorted(
        videos_matched_by_words,
        key=lambda i: (word_counter[i[0]], i[3], 100 - len(i[1])),
        reverse=True,
    )

    # Same for the videos whose title matched characters of the query
    videos_matched_by_characters = Video.objects.filter(
        pk__in=character_counter.keys()
    ).values_list("id", "title", "uploader__username", "views")
    videos_matched_by_characters = sorted(
        videos_matched_by_characters,
        key=lambda i: (character_counter[i[0]], i[3], 100 - len(i[1])),
        reverse=True,
    )

    # Combine all three querySets
    all_matches = list(
        chain(exact_matches, videos_matched_by_words, videos_matched_by_characters)
    )

    # Return the appropriate jsonResponse
    if all_matches:
        return JsonResponse({"matches": all_matches}, status=200)
    else:
        return JsonResponse({}, status=204)


@login_required
def delete_video(request, video_id):
    """Delete a video object."""
    if request.method == "DELETE":
        video = get_video(video_id)
        try:
            video.delete()
        except Exception as e:
            raise Exception(f"An error occurred while trying to delete video:- {e}")

        return JsonResponse({}, status=204)

    else:
        return HttpResponseNotAllowed(["DELETE"])


@login_required
def get_playlists(request):
    """Return a dictionary with the users playlist names as keys
    and lists of all the ids of videos in them as values"""

    # First get the users watchlater list
    playlists = {
        "Watch Later": list(
            request.user.profile.watchlater.all().values_list("id", flat=True)
        )
    }

    # Then add all the created playlists
    playlists.update(
        {
            playlist.name: list(playlist.videos.all().values_list("id", flat=True))
            for playlist in request.user.created_playlists.all()
        }
    )
    playlists = dict(sorted(playlists.items()))

    return JsonResponse(playlists)


@login_required
def update_playlists(request):
    """Add or remove videos from playlists, also create new playlists."""

    # The user is trying to add or remove a video from a playlist
    if request.method == "PUT":
        data = json.loads(request.body)
        playlist_name = data["playlist_name"]
        video = get_video(data["video_id"])
        profile = get_object_or_404(UserProfile, user=request.user)
        if playlist_name == "Watch Later":
            # If the video exists in the list, that means the user is trying to remove
            if profile.watchlater.contains(video):
                try:
                    profile.watchlater.remove(video)
                except Exception as e:
                    raise Exception(
                        f"An error occurred while trying to remove video from user's watch Later list:- {e}"
                    )

                return JsonResponse({"res": "Removed."}, status=200)

            # The user is trying to add
            else:
                try:
                    profile.watchlater.add(video)
                except Exception as e:
                    raise Exception(
                        f"An error occurred while trying to add video to user's watch later list:- {e}"
                    )

                return JsonResponse({"res": "Added."}, status=200)
        else:
            playlist = get_object_or_404(
                PlayList, name=playlist_name, creator=request.user
            )
            if playlist.videos.contains(video):
                try:
                    playlist.videos.remove(video)
                except Exception as e:
                    raise Exception(
                        f"An error occurred while trying to remove video from user's playlist {playlist.name}:- {e}"
                    )

                return JsonResponse({"res": "Removed."}, status=200)
            else:
                try:
                    playlist.videos.add(video)
                except Exception as e:
                    raise Exception(
                        f"An error occurred while trying to add video to user's playlist {playlist.name}:- {e}"
                    )

                return JsonResponse({"res": "Added."}, status=200)

    # The user is trying to create a new playlist and add a video to it
    elif request.method == "POST":
        data = json.loads(request.body)
        video = get_video(data["video_id"])

        # Try to create the playlist and add the video to it in a single transaction, handle exceptions
        try:
            with transaction.atomic():
                new_playlist = PlayList(
                    name=data["new_playlist_name"], creator=request.user
                )
                new_playlist.full_clean()
                new_playlist.save()
                new_playlist.videos.add(video)
        except ValidationError:
            return JsonResponse(
                {"res": "Length of the name must be between 1 and 100 characters"},
                status=400,
            )
        except IntegrityError:
            return JsonResponse({"res": "Playlist already exists."}, status=400)

        except TransactionManagementError as e:
            raise Exception(f"TransactionManagementError:- {e}")
            return JsonResponse(
                {
                    "res": "An error occurred while processing your request. Please try again later."
                },
                status=500,
            )

        return JsonResponse(
            {
                "res": "Playlist created and video added to it.",
                "name": new_playlist.name,
                "slug": new_playlist.slug,
            },
            status=201,
        )
    else:
        return HttpResponseNotAllowed(["PUT", "POST"])


@login_required
def list_videos(request, list_name):
    """Return requested videos in particular lists as JsonResponse."""

    # Get videos for the requested list_name
    if list_name == "liked_videos":
        video_ids = Like.objects.filter(user=request.user).values_list("video")
        videos = Video.objects.filter(pk__in=video_ids).order_by("-timestamp")

    elif list_name == "watchlater":
        profile = get_object_or_404(user=request.user)
        videos = profile.watchlater.all().order_by("-timestamp")

    elif list_name == "uploaded_videos":
        videos = Video.objects.filter(uploader=request.user).order_by("-timestamp")

    else:
        # In the case of created playlists, slug from lists name is used instead of the name
        playlist = get_object_or_404(PlayList, creator=request.user, slug=list_name)
        videos = playlist.videos.all().order_by("-timestamp")
        list_name = playlist.name

    if request.GET.get("start") and request.GET.get("end"):
        start = int(request.GET.get("start"))
        end = int(request.GET.get("end"))
        data = get_data_segment(start, end, videos)

        if data is not None:
            return JsonResponse(
                {list_name: [video.serialize() for video in data]}, status=200
            )
        else:
            return JsonResponse({"list_name": list_name}, status=206)

    return render(request, "youplay/list_videos.html")


@login_required
def delete_playlist(request, playlist_name):
    """delete playlists."""
    if request.method == "DELETE":
        playlist = get_object_or_404(PlayList, name=playlist_name, creator=request.user)
        try:
            playlist.delete()
        except Exception as e:
            raise Exception(
                f"An error occurred while trying to delete playlist {playlist.name}:- {e}"
            )

        return JsonResponse({}, status=204)
    else:
        HttpResponseNotAllowed(["DELETE"])
