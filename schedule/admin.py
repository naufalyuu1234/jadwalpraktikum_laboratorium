from django.contrib import admin
from .models import Schedule, Attendance

@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('title', 'room', 'start_time', 'end_time', 'assistant')
    list_filter = ('room', 'assistant')

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('schedule', 'user', 'booking_time', 'status')
    list_filter = ('status', 'schedule', 'user')