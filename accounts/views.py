from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.sites.shortcuts import get_current_site
from django.db import IntegrityError, transaction
from django.db.transaction import TransactionManagementError
from django.http import HttpResponseNotAllowed, HttpResponseServerError, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from PIL import Image

from .forms import (
    AboutForm,
    CustomPasswordChangeForm,
    CustomUserCreationForm,
    EmailChangeForm,
    UsernameChangeForm,
)
from .models import User, UserProfile


class TokenGenerator(PasswordResetTokenGenerator):
    """Generate a token for activating accounts."""

    def _make_hash_value(self, user, timestamp):
        """Return a hash value based on the users primary key, timestamp and active status."""

        return f"{user.pk}{timestamp}{user.is_active}"


account_activation_token = TokenGenerator()  # Store the token in a variable


def is_valid_image(image):
    """Check if an image is valid or not, returns True if it is, and False if it's not."""
    try:
        img = Image.open(image)
        img.verify()
        return True
    except Exception as e:
        print(e)
        return False


def login_view(request):
    """Authenticate and log an user in."""
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username.lower(), password=password)

        if user is not None:
            login(request, user, backend="django.contrib.auth.backends.ModelBackend")
            return redirect("youplay:index")
        else:
            return render(
                request,
                "accounts/login.html",
                {"message": "Invalid username and/or password."},
            )
    else:
        return render(request, "accounts/login.html")


def logout_view(request):
    """Log an user out"""
    logout(request)
    return redirect("youplay:index")


def register(request):
    """Register an user"""
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()

            # Set the users active status to false until email confirmation
            user.is_active = False
            user.save()

            current_site = get_current_site(request)
            mail_subject = "Activation link has been sent to your email id"
            message = render_to_string(
                "accounts/activation_mail.html",
                {
                    "user": user,
                    "domain": current_site.domain,
                    "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                    "token": account_activation_token.make_token(user),
                },
            )

            # Send a confirmation link to the users email address
            user.email_user(mail_subject, message)

            return render(
                request,
                "accounts/register.html",
                {
                    "message": "An activation link has been sent to your email id, please go to your inbox and confirm by clicking that link to complete your registration. (You might have to look in the spam folder!)",
                    "form": CustomUserCreationForm(),
                },
            )
        else:
            return render(request, "accounts/register.html", {"form": form})

    return render(request, "accounts/register.html", {"form": CustomUserCreationForm()})


def activate(request, uidb64, token):
    """Activate the users account using the specified uid and token."""
    try:
        # If the uid can be decoded the specific user object is retrieved
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        # If a valid user object is returned and the token checks out the users active status is set to true
        user.is_active = True
        user.save()
        return render(
            request,
            "accounts/login.html",
            {
                "message": "Thank you for confirming your registration! Now you can log in."
            },
        )
    else:
        return redirect(
            reverse("accounts:register", args=("Activation link is invalid",))
        )


@login_required
def edit_user_profile(request):
    """Handle user's edit of profile information in the edit_profile page."""

    # All the edit forms
    context = {
        "user_data": request.user,
        "form_username": UsernameChangeForm(instance=request.user),
        "form_email": EmailChangeForm(instance=request.user),
        "form_about": AboutForm(instance=request.user.profile),
        "form_password": CustomPasswordChangeForm(request.user),
    }
    if request.method == "POST":
        # Files attached means that user has uploaded a profile picture
        if request.FILES:
            if is_valid_image(request.FILES["file"]):
                profile = get_object_or_404(UserProfile, user=request.user)
                profile.profile_picture = request.FILES["file"]
                profile.save(update_fields=["profile_picture"])
            else:
                raise Exception("The image file failed validity check.")

            return JsonResponse({"response": "success"})

        # User is trying to update the username
        if "username" in request.POST.keys():
            form = UsernameChangeForm(request.POST, instance=request.user)
            if form.is_valid():
                form.save()
                return redirect("accounts:user_profile")
            else:
                request.user.refresh_from_db()
                context["form_username"] = form
                return render(
                    request, "accounts/user_profile.html", {"context": context}
                )

        # User is trying to update the email address
        elif "email" in request.POST.keys():
            form = EmailChangeForm(request.POST, instance=request.user)
            if form.is_valid():
                form.save()
                return redirect("accounts:user_profile")
            else:
                request.user.refresh_from_db()
                context["form_email"] = form
                return render(
                    request, "accounts/user_profile.html", {"context": context}
                )

        # User is trying to update the about field
        elif "about" in request.POST.keys():
            form = AboutForm(request.POST, instance=request.user.profile)
            if form.is_valid():
                form.save()
                return redirect("accounts:user_profile")
            else:
                request.user.refresh_from_db()
                context["form_about"] = form
                return render(
                    request, "accounts/user_profile.html", {"context": context}
                )

        # User is trying to update the password
        elif (
            "old_password"
            and "new_password1"
            and "new_password2" in request.POST.keys()
        ):
            form = CustomPasswordChangeForm(request.user, data=request.POST)
            if form.is_valid():
                form.save()
                update_session_auth_hash(request, form.user)
                return redirect("accounts:user_profile")
            else:
                request.user.refresh_from_db()
                context["form_password"] = form
                return render(
                    request, "accounts/user_profile.html", {"context": context}
                )

    return render(request, "accounts/user_profile.html", {"context": context})


def delete_account(request):
    """Account deletion by the user"""
    if request.method == "DELETE":
        user = request.user
        try:
            with transaction.atomic():
                # Deactivate the users account and set an unusable password
                user.is_active = False
                user.set_unusable_password()
                user.save()
        except (IntegrityError, TransactionManagementError) as e:
            # Handle the exception
            return HttpResponseServerError(
                f"Error deleting user account:- {str(e)}", status=500
            )
        # Return a response with status code 204
        return JsonResponse({"res": "deleted"}, status=204)
    else:
        return HttpResponseNotAllowed(["DELETE"])
