from django.db import models
from django.conf import settings

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
        is_new = self.pk is None # cek apakah ini data edit atau baru

        # Jika proses edit, ambil data lama dari database
        old_target_class = None
        if not is_new:
            old_instance = Schedule.objects.get(pk=self.pk)
            if old_instance:
                old_target_class = old_instance.target_class

        super().save(*args, **kwargs)

        if is_new or (old_target_class != self.target_class):
            self.refresh_attendance_roster()

    def refresh_attendance_roster(self):
        # Hard wipe: hapus semua attendance lalu bangun ulang dari kelas target saat ini.
        self.attendances.all().delete()

        from authentication.models import CustomUser

        students = CustomUser.objects.filter(kelas=self.target_class, is_staff=False)
        new_attendances = [
            Attendance(schedule=self, user=student, status='ABSENT')
            for student in students
        ]
        Attendance.objects.bulk_create(new_attendances)

    def sync_attendance_roster(self):
        # Refresh peserta: pertahankan booking yang sudah ada, lalu tambahkan peserta baru.
        from authentication.models import CustomUser

        target_students = list(
            CustomUser.objects.filter(kelas=self.target_class, is_staff=False)
        )
        target_student_ids = {student.id for student in target_students}

        existing_attendances = {
            attendance.user_id: attendance
            for attendance in self.attendances.select_related('user').all()
        }

        attendances_to_create = []
        for student in target_students:
            if student.id not in existing_attendances:
                attendances_to_create.append(
                    Attendance(schedule=self, user=student, status='ABSENT')
                )

        if attendances_to_create:
            Attendance.objects.bulk_create(attendances_to_create)

        self.attendances.exclude(user_id__in=target_student_ids).exclude(status='BOOKED').delete()


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