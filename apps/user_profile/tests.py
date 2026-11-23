from io import BytesIO
from PIL import Image
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from apps.user_profile.models import Profile


def create_test_image(format='JPEG', size=(100, 100), color=(255, 0, 0)):
    file_obj = BytesIO()
    image = Image.new('RGB', size=size, color=color)
    image.save(file_obj, format=format)
    file_obj.seek(0)
    ext = 'jpg' if format == 'JPEG' else format.lower()
    return SimpleUploadedFile(f"test_avatar.{ext}", file_obj.read(), content_type=f"image/{ext}")


class ProfileHardeningTests(TestCase):
    def setUp(self):
        self.password = 'StrongP@ssw0rd2026!'
        self.user = User.objects.create_user(
            username='student1',
            email='student1@school.edu',
            password=self.password,
            first_name='Juan',
            last_name='Luna',
        )
        self.profile = Profile.objects.create(
            user=self.user,
            full_name='Juan Luna',
            bio='OJT Trainee',
        )
        self.client.force_login(self.user)
        self.profile_url = reverse('profile:profile')

    def test_profile_update_success(self):
        response = self.client.post(self.profile_url, {
            'first_name': 'Juanito',
            'last_name': 'Luna',
            'email': 'juanito@school.edu',
            'bio': 'Updated software intern bio',
        })
        self.assertRedirects(response, self.profile_url)
        self.user.refresh_from_db()
        self.profile.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Juanito')
        self.assertEqual(self.user.email, 'juanito@school.edu')
        self.assertEqual(self.profile.full_name, 'Juanito Luna')
        self.assertEqual(self.profile.bio, 'Updated software intern bio')

    def test_profile_duplicate_email_rejected(self):
        # Create another student
        User.objects.create_user(
            username='student2',
            email='other@school.edu',
            password=self.password,
        )
        response = self.client.post(self.profile_url, {
            'first_name': 'Juan',
            'last_name': 'Luna',
            'email': 'OTHER@SCHOOL.EDU',  # Case-insensitive clash
            'bio': 'Trying to steal email',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response.context['form'], 'email', 'That email address is already in use by another student account.')

    def test_profile_photo_upload_valid_sanitized(self):
        image = create_test_image('JPEG')
        response = self.client.post(self.profile_url, {
            'first_name': 'Juan',
            'last_name': 'Luna',
            'email': 'student1@school.edu',
            'bio': 'Photo test',
            'profile_image': image,
        })
        self.assertRedirects(response, self.profile_url)
        self.profile.refresh_from_db()
        self.assertTrue(bool(self.profile.profile_image))
        # Ensure file exists and can be opened
        saved_img = Image.open(self.profile.profile_image)
        self.assertEqual(saved_img.format, 'JPEG')

    def test_profile_photo_invalid_type_rejected(self):
        fake_file = SimpleUploadedFile("malicious.sh", b"#!/bin/bash\necho bad", content_type="text/x-sh")
        response = self.client.post(self.profile_url, {
            'first_name': 'Juan',
            'last_name': 'Luna',
            'email': 'student1@school.edu',
            'bio': 'Malicious file test',
            'profile_image': fake_file,
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('profile_image', response.context['form'].errors)

    def test_profile_photo_too_large_rejected(self):
        # 3MB oversized payload
        large_bytes = b'a' * (3 * 1024 * 1024)
        large_file = SimpleUploadedFile("huge.jpg", large_bytes, content_type="image/jpeg")
        response = self.client.post(self.profile_url, {
            'first_name': 'Juan',
            'last_name': 'Luna',
            'email': 'student1@school.edu',
            'bio': 'Large file test',
            'profile_image': large_file,
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('profile_image', response.context['form'].errors)
