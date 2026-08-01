from django.contrib.auth.backends import ModelBackend

from .models import CustomUser


class IdentifierBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        role = kwargs.get('role')
        identifier = kwargs.get('identifier') or username

        if not role or not identifier or password is None:
            return None

        if role == 'praktikan':
            lookup = {'role': 'praktikan', 'npm': identifier}
        elif role == 'asisten':
            lookup = {'role': 'asisten', 'assistant_id': identifier}
        else:
            return None

        try:
            user = CustomUser.objects.get(**lookup)
        except CustomUser.DoesNotExist:
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user

        return None