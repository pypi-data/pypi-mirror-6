
from .models import User, Role

class SaasUserBackend(object):

    def authenticate(self, username=None, password=None, **kwargs):
        if username is None:
            try:
                username = kwargs['email']
            except KeyError:
                return
        email = User.objects.normalize_email(username)
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return None
        else:
            if user.check_password(password):
                return user.get_default_role()

    def get_user(self, user_id):
        try:
            return Role._default_manager.get(pk=user_id)
        except Role.DoesNotExist:
            return None

