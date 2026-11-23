from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from apps.user_profile.models import Profile
from apps.user_settings.models import UserSettings


class RegistrationTests(TestCase):
    def setUp(self):
        self.register_url = reverse('register:register')

    def test_registration_success(self):
        response = self.client.post(self.register_url, {
            'first_name': 'Maria',
            'last_name': 'Santos',
            'username': 'mariasantos',
            'email': 'maria@university.edu.ph',
            'password': 'SecureP@ssword123!',
            'password_confirm': 'SecureP@ssword123!',
        })
        self.assertRedirects(response, reverse('home:home'))
        user = User.objects.filter(username='mariasantos').first()
        self.assertIsNotNone(user)
        self.assertEqual(user.email, 'maria@university.edu.ph')
        self.assertTrue(Profile.objects.filter(user=user).exists())
        self.assertTrue(UserSettings.objects.filter(user=user).exists())

    def test_registration_duplicate_username_case_insensitive(self):
        User.objects.create_user(
            username='juandelacruz',
            email='juan@univ.edu',
            password='SecureP@ssword123!',
        )
        response = self.client.post(self.register_url, {
            'first_name': 'Juan',
            'last_name': 'Dela Cruz',
            'username': 'JuanDelaCruz',  # Same username with different casing
            'email': 'another@univ.edu',
            'password': 'SecureP@ssword123!',
            'password_confirm': 'SecureP@ssword123!',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response.context['form'], 'username', 'That username is already taken. Please choose another.')

    def test_registration_duplicate_email_case_insensitive(self):
        User.objects.create_user(
            username='user1',
            email='student@school.edu',
            password='SecureP@ssword123!',
        )
        response = self.client.post(self.register_url, {
            'first_name': 'Student',
            'last_name': 'Two',
            'username': 'user2',
            'email': 'STUDENT@SCHOOL.EDU',  # Same email with uppercase
            'password': 'SecureP@ssword123!',
            'password_confirm': 'SecureP@ssword123!',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response.context['form'], 'email', 'An account with that email address already exists.')

    def test_registration_password_too_short(self):
        response = self.client.post(self.register_url, {
            'first_name': 'Short',
            'last_name': 'Pass',
            'username': 'shortpass',
            'email': 'short@univ.edu',
            'password': 'Pass1!',  # Only 6 characters (< 10)
            'password_confirm': 'Pass1!',
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('password', response.context['form'].errors)

    def test_registration_password_mismatch(self):
        response = self.client.post(self.register_url, {
            'first_name': 'Mismatch',
            'last_name': 'User',
            'username': 'mismatchuser',
            'email': 'mismatch@univ.edu',
            'password': 'SecureP@ssword123!',
            'password_confirm': 'DifferentP@ssword123!',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response.context['form'], 'password_confirm', 'Passwords do not match.')

    def test_registration_weak_password_rejected(self):
        response = self.client.post(self.register_url, {
            'first_name': 'Numeric',
            'last_name': 'Only',
            'username': 'numericpass',
            'email': 'numeric@univ.edu',
            'password': '123456789012',  # Entirely numeric
            'password_confirm': '123456789012',
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('password', response.context['form'].errors)
