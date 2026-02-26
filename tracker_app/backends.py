from django.contrib.auth.backends import BaseBackend
from .models import CustomUser


class EmailAuthBackend(BaseBackend):
    """
    Custom authentication backend that allows users to log in using their email address.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # Try to find user by email
            user = CustomUser.objects.get(email=username)
            if user.check_password(password) and user.is_active:
                return user
        except CustomUser.DoesNotExist:
            # Try to find user by username as fallback
            try:
                user = CustomUser.objects.get(username=username)
                if user.check_password(password) and user.is_active:
                    return user
            except CustomUser.DoesNotExist:
                return None
        return None

    def get_user(self, user_id):
        try:
            return CustomUser.objects.get(pk=user_id)
        except CustomUser.DoesNotExist:
            return None