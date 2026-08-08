from django.contrib import admin
from .models import Schedule, Attendance


class AttendanceInline(admin.TabularInline):
    model = Attendance
    extra = 0
    readonly_fields = ('booking_time',)
    autocomplete_fields = ('user',)


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('title', 'target_class', 'room', 'start_time', 'end_time', 'assistant')
    list_filter = ('target_class', 'room', 'assistant')
    search_fields = ('title', 'target_class', 'room', 'assistant__username', 'assistant__first_name')
    ordering = ('-start_time',)
    inlines = [AttendanceInline]


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('schedule', 'user', 'status', 'booking_time')
    list_filter = ('status', 'schedule__target_class', 'schedule__room')
    search_fields = (
        'user__username', 
        'user__npm', 
        'user__first_name', 
        'user__last_name', 
        'schedule__title'
    )
    # Mengatasi N+1 Query Problem di Django Admin
    list_select_related = ('schedule', 'user')
    readonly_fields = ('booking_time',)