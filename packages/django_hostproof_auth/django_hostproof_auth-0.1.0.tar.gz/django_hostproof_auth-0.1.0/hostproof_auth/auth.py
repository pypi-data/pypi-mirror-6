from django.contrib.auth.models import check_password
from hostproof_auth.models import User

class ModelBackend(object):
    def authenticate(self, username=None, challenge=None):
        if username and challenge:
            try:
                user = User.objects.get(username=username)
                if check_password(challenge, user.challenge):
                    return user
            except User.DoesNotExist:
                pass
        return None
    
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
