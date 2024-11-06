from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.urls import reverse
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    list_display = (
        'email',
        'user_type',
        'hit_count',
        'last_hit_time',
        'is_staff',
        'is_superuser',
    )
    list_filter = ('user_type', 'is_staff', 'is_superuser')
    search_fields = ('email',)

    # Correct the ordering to use a field that exists in the model
    ordering = ('email',)  # Update this to 'email' instead of 'username'

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'user_type', 'hit_count', 'last_hit_time')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    readonly_fields = ('hit_count', 'last_hit_time')


# Register the CustomUser model with the admin site
admin.site.register(CustomUser, CustomUserAdmin)
