from django.db import models
from django.conf import settings

# Create your models here.
class Attendance(models.Model):
    STATUS_CHOICES = [
        ('BOOKED', 'Booked'),
        ('ATTENDED', 'Attended'),
        ('ABSENT', 'Absent'),
    ]

    schedule = models.ForeignKey('Schedule', on_delete=models.CASCADE, related_name='attendances')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='attendances')
    booking_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='BOOKED')

    def __str__(self):
        return f"{self.user.username} - {self.schedule.title} - {self.status}"

class Schedule(models.Model):
    title = models.CharField(max_length=100)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    room = models.CharField(max_length=50)
    assistant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='assisted_schedules')

    def __str__(self):
        return f"{self.title} ({self.room})"