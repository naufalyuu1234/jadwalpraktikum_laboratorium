from django.contrib import admin
from authentication.models import CustomUser
from django.contrib.auth.admin import UserAdmin

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'npm', 'assistant_id', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_active')
    search_fields = ('username', 'email', 'npm', 'assistant_id', 'first_name', 'last_name')
    fieldsets = UserAdmin.fieldsets + (
        ('Informasi Laboratorium', {'fields': ('role', 'npm', 'assistant_id')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Informasi Laboratorium', {'fields': ('role', 'npm', 'assistant_id')}),
    )
    

# mendaftarkan model
admin.site.register(CustomUser, CustomUserAdmin)