from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from authentication.models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = (
        'username', 
        'email', 
        'first_name', 
        'last_name', 
        'role', 
        'npm', 
        'assistant_id', 
        'kelas', 
        'is_staff'
    )
    list_filter = ('role', 'is_staff', 'is_active', 'kelas')
    search_fields = ('username', 'email', 'npm', 'assistant_id', 'first_name', 'last_name', 'kelas')
    
    fieldsets = UserAdmin.fieldsets + (
        ('Informasi Laboratorium', {'fields': ('role', 'npm', 'assistant_id', 'kelas')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Informasi Laboratorium', {'fields': ('role', 'npm', 'assistant_id', 'kelas')}),
    )