from django.contrib.auth.models import User
from django.db import models


class Profile(models.Model):
    """
    Profile feature's own data — one-to-one with Django's User.
    Kept separate from the User model itself so Profile can evolve
    (bio, avatar, etc.) without touching Django's built-in auth tables.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    full_name = models.CharField(max_length=150, blank=True)
    bio = models.TextField(blank=True)
    profile_image = models.ImageField(upload_to='profile/', blank=True, null=True)

    class Meta:
        db_table = 'profile'

    def __str__(self):
        return self.user.username
