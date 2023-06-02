from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Video


class UploadForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = ["title", "description", "thumbnail", "video", "uploader"]

        widgets = {
            "video": forms.FileInput(
                attrs={
                    "accept": ".mp4, .mkv, .mov, .wmv, .avi,  .3gp, .flv, .mkv, .m4a, .webm, .ogg"
                }
            ),
            "thumbnail": forms.FileInput(
                attrs={"accept": ".jpg, .jpeg, .png, .bmp, .gif, .tiff"}
            ),
            "uploader": forms.HiddenInput(attrs={"required": False}),
        }


class EditDescriptionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(EditDescriptionForm, self).__init__(*args, **kwargs)
        self.fields["description"].required = True

    class Meta:
        model = Video
        fields = ["description"]
