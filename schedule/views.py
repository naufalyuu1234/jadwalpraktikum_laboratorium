from datetime import timedelta
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.core.exceptions import PermissionDenied
from .models import FAQ

from .forms import ScheduleForm
from .models import Attendance, Schedule


def can_manage_schedule(user):
    # Menggunakan property is_asisten dari CustomUser model
    return user.is_authenticated and user.is_asisten


def schedule_list(request):
    now = timezone.now()

    # 1. Ambil hanya jadwal yang belum selesai (aktif)
    schedules = (
        Schedule.objects.select_related('assistant')
        .filter(end_time__gte=now)
        .order_by('start_time')
    )

    # 2. Metrik Dashboard berdasarkan jadwal aktif
    schedule_count = schedules.count()
    room_count = schedules.values('room').distinct().count()
    
    # Hanya hitung mahasiswa yang statusnya benar-benar sudah BOOKED pada jadwal aktif
    booking_count = Attendance.objects.filter(
        schedule__in=schedules,
        status=Attendance.Status.BOOKED
    ).count()

    return render(
        request,
        'schedule/list.html',
        {
            'schedules': schedules,
            'can_create_schedule': can_manage_schedule(request.user),
            'schedule_count': schedule_count,
            'room_count': room_count,
            'booking_count': booking_count,
        },
    )


@login_required
def schedule_create(request):
    if not can_manage_schedule(request.user):
        messages.error(request, 'Kamu tidak punya izin untuk menambah jadwal.')
        return redirect('schedule:list')

    if request.method == 'POST':
        form = ScheduleForm(request.POST)
        if form.is_valid():
            schedule = form.save(commit=False)
            schedule.assistant = request.user
            schedule.save()
            messages.success(request, 'Jadwal berhasil ditambahkan.')
            return redirect('schedule:detail', schedule_id=schedule.id)
    else:
        form = ScheduleForm()

    return render(request, 'schedule/create.html', {'form': form})

@login_required
@require_POST
def schedule_delete(request, pk):
  schedule = get_object_or_404(Schedule, pk=pk)

  # Otorisasi: Hanya asisten pemilik atau staf admin yang boleh menghapus
  if request.user != schedule.assistant and not request.user.is_staff:
    messages.error(
        request, 'Anda tidak memiliki hak akses untuk menghapus jadwal ini.'
    )
    raise PermissionDenied

  schedule_title = schedule.title
  schedule.delete()

  messages.success(
      request, f"Jadwal praktikum '{schedule_title}' berhasil dihapus."
  )
  return redirect('schedule:list')

def schedule_detail(request, schedule_id):
    schedule = get_object_or_404(Schedule, id=schedule_id)
    attendances = schedule.attendances.select_related('user').all().order_by('booking_time', 'id')
    return render(
        request,
        'schedule/detail.html',
        {
            'schedule': schedule,
            'attendances': attendances,
            'can_manage_schedule': can_manage_schedule(request.user),
        },
    )


@login_required
@require_POST
def schedule_refresh_participants(request, schedule_id):
    if not can_manage_schedule(request.user):
        messages.error(request, 'Kamu tidak punya izin untuk me-refresh peserta jadwal.')
        return redirect('schedule:detail', schedule_id=schedule_id)

    schedule = get_object_or_404(Schedule, id=schedule_id)
    schedule.sync_attendance_roster()
    messages.success(request, 'Daftar peserta berhasil di-refresh tanpa menghapus booking yang sudah ada.')
    return redirect('schedule:detail', schedule_id=schedule.id)


@login_required
@require_POST
def schedule_hard_wipe(request, schedule_id):
    if not can_manage_schedule(request.user):
        messages.error(request, 'Kamu tidak punya izin untuk melakukan hard wipe jadwal.')
        return redirect('schedule:detail', schedule_id=schedule_id)

    schedule = get_object_or_404(Schedule, id=schedule_id)
    schedule.refresh_attendance_roster()
    messages.success(request, 'Attendance berhasil di-reset total dari kelas target saat ini.')
    return redirect('schedule:detail', schedule_id=schedule.id)


@login_required
@require_POST  # Wajib POST untuk mutasi data booking
def book_practicum(request, schedule_id):
    schedule = get_object_or_404(Schedule, id=schedule_id)
    now = timezone.now()

    # Validasi Batas Waktu H-1 (Hanya untuk Mahasiswa biasa / Praktikan)
    if not request.user.is_staff:
        if schedule.start_time - now < timedelta(days=1):
            messages.error(request, "Maaf, batas waktu booking H-1 sudah lewat!")
            return redirect('schedule:detail', schedule_id=schedule.id)

    attendance = Attendance.objects.filter(schedule=schedule, user=request.user).first()

    if not attendance:
        messages.error(request, "Anda tidak terdaftar di dalam daftar kelas untuk praktikum ini!")
        return redirect('schedule:list')

    if attendance.status == 'BOOKED':
        messages.info(request, "Kamu sudah melakukan booking untuk sesi ini.")
    else:
        attendance.status = 'BOOKED'
        attendance.booking_time = now
        attendance.save()
        messages.success(request, "Booking praktikum berhasil!")

    return redirect('schedule:detail', schedule_id=schedule.id)

def faq_view(request):
  faqs = FAQ.objects.filter(is_active=True).order_by('order', '-created_at')
  return render(request, 'schedule/faq.html', {'faqs': faqs})