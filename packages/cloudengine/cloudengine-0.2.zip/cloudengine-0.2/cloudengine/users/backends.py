from __future__ import unicode_literals
from cloudengine.users.models import AppUser

class ModelBackend(object):
    
    def authenticate(self, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get(AppUser.USERNAME_FIELD)
        try:
            user = AppUser.objects.get_by_natural_key(username)
            if user.check_password(password):
                return user
        except AppUser.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return AppUser.objects.get(pk=user_id)
        except AppUser.DoesNotExist:
            return None
