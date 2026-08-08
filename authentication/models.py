from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    class Role(models.TextChoices):
        PRAKTIKAN = 'PRAKTIKAN', 'Praktikan'
        ASISTEN = 'ASISTEN', 'Asisten'

    role = models.CharField(
        max_length=20, 
        choices=Role.choices, 
        default=Role.PRAKTIKAN
    )
    npm = models.CharField(
        max_length=20, 
        unique=True, 
        blank=True, 
        null=True
    )
    assistant_id = models.CharField(
        max_length=20, 
        unique=True, 
        blank=True, 
        null=True
    )
    kelas = models.CharField(
        max_length=10, 
        blank=True, 
        help_text="Contoh: 2IA06"
    )

    @property
    def is_asisten(self):
        return self.role == self.Role.ASISTEN or self.is_staff

    @property
    def is_praktikan(self):
        return self.role == self.Role.PRAKTIKAN

    def __str__(self):
        return self.get_full_name() or self.username