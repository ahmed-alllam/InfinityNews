from django.contrib.auth.models import AbstractUser
from django.db import models


class UserProfile(AbstractUser):
    profile_photo = models.ImageField(null=True)
