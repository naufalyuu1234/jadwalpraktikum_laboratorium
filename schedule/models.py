from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model

class Schedule(models.Model):
    title = models.CharField(max_length=200)
    room = models.CharField(max_length=50)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    assistant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='schedules')
    target_class = models.CharField(max_length=10, help_text="Kelas yang wajib ikut, contoh: 2IA06")

    def __str__(self):
        return f"{self.title} - {self.target_class} ({self.room})"

    def save(self, *args, **kwargs):
        is_new = self.pk is None # Cek apakah ini data edit atau baru

        # Ambil data target_class lama secara aman jika ini proses edit
        old_target_class = None
        if not is_new:
            old_instance = Schedule.objects.filter(pk=self.pk).first()
            if old_instance:
                old_target_class = old_instance.target_class

        # Simpan jadwal utama terlebih dahulu
        super().save(*args, **kwargs)

        # Jalankan Hard Wipe jika jadwal baru ATAU target_class diubah
        if is_new or (old_target_class != self.target_class):
            self.refresh_attendance_roster()

    def refresh_attendance_roster(self):    
        # 1. Hard Wipe: Hapus presensi lama yang terikat dengan jadwal ini
        self.attendances.all().delete()

        # 2. Ambil model User secara dinamis
        User = get_user_model()

        # 3. Cari praktikan dengan kelas yang sesuai (Gunakan Uppercase jika choice di model 'PRAKTIKAN')
        students = User.objects.filter(kelas=self.target_class, role='PRAKTIKAN')
        
        # 4. Bulk Create untuk efisiensi query
        new_attendances = [
            Attendance(schedule=self, user=student, status='ABSENT')
            for student in students
        ]
        Attendance.objects.bulk_create(new_attendances)


class Attendance(models.Model):
    STATUS_CHOICES = [
        ('BOOKED', 'Booked'),
        ('ABSENT', 'Absent'),  
    ]

    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, related_name='attendances')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='attendances')
    booking_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='ABSENT')

    class Meta:
        unique_together = ('schedule', 'user') 

    def __str__(self):
        return f"{self.user.username} - {self.schedule.title} ({self.status})"