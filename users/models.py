from django.contrib.auth.models import AbstractUser
from django.db import models

from news.models import Category


class UserProfile(AbstractUser):
    profile_photo = models.ImageField(null=True)
    favourite_categories = models.ManyToManyField(Category)
