from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from myapp.models import CustomUser


class CustomUserAdmin(UserAdmin):
    list_display = (
        "email",
        "user_type",
        "hit_count",
        "last_hit_time",
        "is_staff",
        "is_superuser",
    )
    list_filter = ("user_type", "is_staff", "is_superuser")
    search_fields = ("email",)

    ordering = ("email",)

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Personal info",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "user_type",
                    "hit_count",
                    "last_hit_time",
                )
            },
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )

    readonly_fields = ("hit_count", "last_hit_time")


admin.site.register(CustomUser, CustomUserAdmin)
