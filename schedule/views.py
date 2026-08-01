from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
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
        },
    )

@login_required
def book_practicum(request, schedule_id):
    schedule = get_object_or_404(Schedule, id=schedule_id)
    now = timezone.now()
    
    # 1. Validasi Batas Waktu H-1 (Hanya untuk Mahasiswa)
    if not request.user.is_staff: 
        if schedule.start_time - now < timedelta(days=1):
            messages.error(request, "Maaf, batas waktu booking H-1 sudah lewat!")
            return redirect('schedule:detail', schedule_id=schedule.id)
            
    # 2. Proses Pembuatan Data Absen ( get_or_create )
    attendance, created = Attendance.objects.get_or_create(
        schedule=schedule,
        user=request.user,
        defaults={'status': 'BOOKED', 'booking_time': now}
    )
    
    if not created:
        messages.info(request, "Kamu sudah melakukan booking untuk sesi ini.")
    else:
        messages.success(request, "Booking praktikum berhasil!")
        
    return redirect('schedule:detail', schedule_id=schedule.id)