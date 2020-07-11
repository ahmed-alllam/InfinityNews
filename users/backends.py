from django.contrib.auth.backends import BaseBackend

from users.models import UserProfile


class GuestUserBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None):
        try:
            user = UserProfile.objects.get(username=username)
            if not user.has_usable_password():
                return user

            if user.check_password(password) is True:
                return user

            return None
        except UserProfile.DoesNotExist:
            return None
