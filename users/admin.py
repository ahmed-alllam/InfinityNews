from django.contrib import admin
from django.contrib.auth.models import Group

from users.models import UserProfile

admin.site.unregister(Group)
admin.site.register(UserProfile)
