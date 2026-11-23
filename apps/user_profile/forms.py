import os
from io import BytesIO
from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from PIL import Image

from .models import Profile

MAX_UPLOAD_SIZE = 2 * 1024 * 1024  # 2 MB
ALLOWED_IMAGE_TYPES = {'image/jpeg', 'image/png', 'image/webp'}
ALLOWED_IMAGE_FORMATS = {'JPEG', 'PNG', 'WEBP'}


class ProfileForm(forms.ModelForm):
    first_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-input', 'id': 'id_first_name'}),
    )
    last_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-input', 'id': 'id_last_name'}),
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-input', 'id': 'id_email'}),
    )

    class Meta:
        model = Profile
        fields = ['bio', 'profile_image']
        widgets = {
            'bio': forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'id': 'id_bio'}),
            'profile_image': forms.FileInput(attrs={'id': 'id_profile_image', 'accept': 'image/jpeg,image/png,image/webp'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user:
            self.fields['first_name'].initial = self.user.first_name
            self.fields['last_name'].initial = self.user.last_name
            self.fields['email'].initial = self.user.email

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if not email:
            raise ValidationError('School email is required.')

        user_query = User.objects.filter(email__iexact=email)
        if self.user and self.user.pk:
            user_query = user_query.exclude(pk=self.user.pk)

        if user_query.exists():
            raise ValidationError('That email address is already in use by another student account.')
        return email

    def clean_profile_image(self):
        image = self.cleaned_data.get('profile_image')
        if not image or isinstance(image, bool):
            return image

        # Only process if a new file was uploaded
        if hasattr(image, 'size'):
            if image.size > MAX_UPLOAD_SIZE:
                raise ValidationError('The uploaded image exceeds the 2 MB size limit.')

            content_type = getattr(image, 'content_type', '')
            if content_type and content_type.lower() not in ALLOWED_IMAGE_TYPES:
                raise ValidationError('Only JPG, PNG, and WebP images are permitted.')

            # Inspect and sanitize image content with Pillow
            try:
                img = Image.open(image)
                img.verify()  # Verify image integrity
            except Exception:
                raise ValidationError('The uploaded file is not a valid image.')

            # Re-open for sanitization (verify() leaves stream in unusable state)
            image.seek(0)
            img = Image.open(image)
            img_format = img.format.upper() if img.format else ''
            if img_format not in ALLOWED_IMAGE_FORMATS:
                raise ValidationError(f'Unsupported image format ({img_format}). Only JPG, PNG, and WebP are allowed.')

            # Re-save to strip EXIF and potentially dangerous payload metadata
            output = BytesIO()
            save_format = 'JPEG' if img_format == 'JPEG' else img_format
            if save_format == 'JPEG' and img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')
            img.save(output, format=save_format, quality=85)
            output.seek(0)

            # Generate safe sanitized filename
            ext = 'jpg' if save_format == 'JPEG' else save_format.lower()
            safe_filename = f"avatar_{self.user.username}_{ext}.{ext}"
            return ContentFile(output.read(), name=safe_filename)

        return image

    def save(self, commit=True):
        profile = super().save(commit=False)
        if self.user:
            self.user.first_name = self.cleaned_data['first_name'].strip()
            self.user.last_name = self.cleaned_data['last_name'].strip()
            self.user.email = self.cleaned_data['email'].strip().lower()
            self.user.save()

            full_name = f"{self.user.first_name} {self.user.last_name}".strip()
            profile.full_name = full_name

        if commit:
            profile.save()
        return profile
