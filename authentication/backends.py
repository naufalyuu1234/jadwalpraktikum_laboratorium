from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

User = get_user_model()


class IdentifierBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        role = kwargs.get('role')
        identifier = kwargs.get('identifier') or username

        if not role or not identifier or password is None:
            return None

        # Normalisasi role ke UPPERCASE agar sesuai dengan User.Role Enum
        role_upper = str(role).upper()

        if role_upper == User.Role.PRAKTIKAN:
            lookup = {'role': User.Role.PRAKTIKAN, 'npm': identifier.strip()}
        elif role_upper == User.Role.ASISTEN:
            lookup = {'role': User.Role.ASISTEN, 'assistant_id': identifier.strip()}
        else:
            return None

        try:
            user = User.objects.get(**lookup)
        except User.DoesNotExist:
            return None
        except User.MultipleObjectsReturned:
            # Mengambil data pertama jika terjadi duplikasi akibat ketidakmampuan constraint di DB lama
            user = User.objects.filter(**lookup).first()

        if user and user.check_password(password) and self.user_can_authenticate(user):
            return user

        return None