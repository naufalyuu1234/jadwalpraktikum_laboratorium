from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class CustomUser(AbstractUser):
    # variable pilihan praktikan dan asisten
    ROLE_CHOICES = (('praktikan', 'Praktikan'), ('asisten', 'Asisten'))
    # Definisikan field role
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='praktikan')
    npm = models.CharField(max_length=20, unique=True, blank=True, null=True, db_index=True)
    assistant_id = models.CharField(max_length=20, unique=True, blank=True, null=True, db_index=True)

    def __str__(self):
        return self.get_full_name() or self.username
    
    