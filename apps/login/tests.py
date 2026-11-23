from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from axes.models import AccessAttempt


class LoginAndSecurityTests(TestCase):
    def setUp(self):
        self.username = 'teststudent'
        self.password = 'StrongP@ssw0rd2026!'
        self.user = User.objects.create_user(
            username=self.username,
            email='student@example.edu',
            password=self.password,
            first_name='Student',
            last_name='Tester',
        )
        self.login_url = reverse('login:login')
        self.logout_url = reverse('login:logout')

    def test_login_success(self):
        response = self.client.post(self.login_url, {
            'username': self.username,
            'password': self.password,
        })
        self.assertRedirects(response, reverse('home:home'))
        self.assertTrue('_auth_user_id' in self.client.session)

    def test_login_failure(self):
        response = self.client.post(self.login_url, {
            'username': self.username,
            'password': 'WrongPassword123!',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid username or password')
        self.assertFalse('_auth_user_id' in self.client.session)

    def test_login_safe_redirect(self):
        response = self.client.post(f"{self.login_url}?next=/profile/", {
            'username': self.username,
            'password': self.password,
        })
        self.assertRedirects(response, '/profile/')

    def test_login_malicious_redirect_prevented(self):
        response = self.client.post(f"{self.login_url}?next=https://attacker-site.com/steal", {
            'username': self.username,
            'password': self.password,
        })
        # Must ignore malicious external target and redirect to safe dashboard
        self.assertRedirects(response, reverse('home:home'))

    def test_logout_get_rejected(self):
        self.client.force_login(self.user)
        response = self.client.get(self.logout_url)
        # GET is rejected with 405 Method Not Allowed
        self.assertEqual(response.status_code, 405)

    def test_logout_post_success(self):
        self.client.force_login(self.user)
        response = self.client.post(self.logout_url)
        self.assertRedirects(response, self.login_url)
        self.assertFalse('_auth_user_id' in self.client.session)

    def test_login_lockout_after_failures(self):
        # 5 consecutive failures triggers lockout
        for _ in range(5):
            self.client.post(self.login_url, {
                'username': self.username,
                'password': 'WrongPassword123!',
            })

        # 6th attempt should be locked out with HTTP 429
        response = self.client.post(self.login_url, {
            'username': self.username,
            'password': self.password,
        })
        self.assertEqual(response.status_code, 429)
        self.assertContains(response, 'Too Many Failed Sign-In Attempts', status_code=429)

    def test_password_change_flow(self):
        self.client.force_login(self.user)
        new_password = 'NewSuperP@ssw0rd2026!'
        response = self.client.post(reverse('login:password_change'), {
            'old_password': self.password,
            'new_password1': new_password,
            'new_password2': new_password,
        })
        self.assertRedirects(response, reverse('login:password_change_done'))
        # Confirm user can log in with new password
        self.client.logout()
        login_response = self.client.post(self.login_url, {
            'username': self.username,
            'password': new_password,
        })
        self.assertRedirects(login_response, reverse('home:home'))
