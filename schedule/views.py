from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.utils import timezone
from datetime import timedelta
from .models import Schedule, Attendance
from .forms import ScheduleForm


def can_manage_schedule(user):
    return user.is_authenticated and (user.is_staff or getattr(user, 'role', '') == 'asisten')


def schedule_list(request):
    schedules = Schedule.objects.select_related('assistant').all().order_by('start_time')
    schedule_count = schedules.count()
    room_count = schedules.values('room').distinct().count()
    booking_count = Attendance.objects.count()
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
@require_POST
def book_practicum(request, schedule_id):
    schedule = get_object_or_404(Schedule, id=schedule_id)
    now = timezone.now()
    
    # Validasi Batas Waktu H-1 (Hanya untuk Mahasiswa biasa)
    if not request.user.is_staff:
        if schedule.start_time - now < timedelta(days=1):
            messages.error(request, "Maaf, batas waktu booking H-1 sudah lewat!")
            return redirect('schedule:detail', schedule_id=schedule.id)
            
    # 2. Cari data absensi mahasiswa yang sudah di-generate otomatis sebelumnya
    attendance = Attendance.objects.filter(schedule=schedule, user=request.user).first()
    
    # Jika mahasiswa kelas lain mencoba tembak URL booking secara ilegal
    if not attendance:
        messages.error(request, "Anda tidak terdaftar di dalam daftar kelas untuk praktikum ini!")
        return redirect('schedule:list')
        
    # Proses Uji Status & Update Data
    if attendance.status == 'BOOKED':
        messages.info(request, "Kamu sudah melakukan booking untuk sesi ini.")
    else:
        # Ubah status dari ABSENT menjadi BOOKED
        attendance.status = 'BOOKED'
        attendance.booking_time = now
        attendance.save() # Menyimpan perubahan status ke database
        messages.success(request, "Booking praktikum berhasil!")
        
    return redirect('schedule:detail', schedule_id=schedule.id)