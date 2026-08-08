from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

User = get_user_model()


class IdentifierBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        role = kwargs.get('role')
        identifier = kwargs.get('identifier') or username

        if not role or not identifier or password is None:
            return None

        role_upper = str(role).upper()

        if role_upper == User.Role.PRAKTIKAN:
            lookup = {'role': User.Role.PRAKTIKAN, 'npm': identifier}
        elif role_upper == User.Role.ASISTEN:
            lookup = {'role': User.Role.ASISTEN, 'assistant_id': identifier}
        else:
            return None

        try:
            user = User.objects.get(**lookup)
        except (User.DoesNotExist, User.MultipleObjectsReturned):
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user

        return None