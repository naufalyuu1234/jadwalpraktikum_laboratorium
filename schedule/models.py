from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model


class Schedule(models.Model):
    title = models.CharField(max_length=200)
    room = models.CharField(max_length=50)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    assistant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='schedules'
    )
    target_class = models.CharField(
        max_length=10, 
        help_text="Kelas yang wajib ikut, contoh: 2IA06"
    )

    def __str__(self):
        return f"{self.title} - {self.target_class} ({self.room})"

    def save(self, *args, **kwargs):
        # 1. Normalisasi string target_class ke uppercase
        if self.target_class:
            self.target_class = self.target_class.strip().upper()

        is_new = self.pk is None

        # 2. Ambil target_class lama jika ini proses update
        old_target_class = None
        if not is_new:
            old_instance = Schedule.objects.filter(pk=self.pk).first()
            if old_instance:
                old_target_class = old_instance.target_class

        super().save(*args, **kwargs)

        # 3. Jalankan Hard Wipe jika jadwal baru ATAU target_class diubah
        if is_new or (old_target_class != self.target_class):
            self.refresh_attendance_roster()

    def refresh_attendance_roster(self):
        """Hard Wipe: Hapus seluruh presensi lama dan buat ulang dari awal."""
        self.attendances.all().delete()

        User = get_user_model()
        students = User.objects.filter(
            kelas__iexact=self.target_class, 
            role=User.Role.PRAKTIKAN
        )

        new_attendances = [
            Attendance(schedule=self, user=student, status=Attendance.Status.ABSENT)
            for student in students
        ]
        Attendance.objects.bulk_create(new_attendances)

    def sync_attendance_roster(self):
        """Soft Refresh: Hanya tambahkan mahasiswa baru tanpa menghapus data booking yang ada."""
        User = get_user_model()
        
        # Ambil daftar ID user yang sudah terdaftar di presensi jadwal ini
        existing_user_ids = set(self.attendances.values_list('user_id', flat=True))

        # Cari mahasiswa kelas target yang belum masuk daftar presensi
        new_students = User.objects.filter(
            kelas__iexact=self.target_class, 
            role=User.Role.PRAKTIKAN
        ).exclude(id__in=existing_user_ids)

        new_attendances = [
            Attendance(schedule=self, user=student, status=Attendance.Status.ABSENT)
            for student in new_students
        ]
        Attendance.objects.bulk_create(new_attendances)


class Attendance(models.Model):
    # Menggunakan TextChoices agar type-safe
    class Status(models.TextChoices):
        BOOKED = 'BOOKED', 'Booked'
        ABSENT = 'ABSENT', 'Absent'

    schedule = models.ForeignKey(
        Schedule, 
        on_delete=models.CASCADE, 
        related_name='attendances'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='attendances'
    )
    booking_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=10, 
        choices=Status.choices, 
        default=Status.ABSENT
    )

    class Meta:
        # Menggunakan UniqueConstraint modern menggantikan unique_together
        constraints = [
            models.UniqueConstraint(
                fields=['schedule', 'user'], 
                name='unique_schedule_user'
            )
        ]

    def __str__(self):
        return f"{self.user.username} - {self.schedule.title} ({self.status})"

# FAQ MODELS
class FAQ(models.Model):
    question = models.CharField(
        max_length=255,
        help_text="Tulis pertanyaan ringkas dan jelas"
    )
    answer = models.TextField(
        help_text="Jawaban lengkap"
    )
    order = models.PositiveIntegerField(
        default=0,
        help_text="Prioritas urutan tampil (contoh: 1, 2, 3)"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Centang untuk menampilkan website"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', '-created_at']
        verbose_name = 'FAQ'
        verbose_name_plural = "Daftar FAQ"

    def __str__(self):
        return f"{self.order}. {self.question}"