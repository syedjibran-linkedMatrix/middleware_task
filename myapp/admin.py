from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.urls import reverse
from .models import CustomUser, APIRequest

class APIRequestInline(admin.TabularInline):
    model = APIRequest
    extra = 0
    can_delete = False
    readonly_fields = ('timestamp',)
    ordering = ('-timestamp',)
    max_num = 10  # Show only last 10 requests
    
    def has_add_permission(self, request, obj=None):
        return False

class CustomUserAdmin(UserAdmin):
    ordering = ('email',)
    
    list_display = (
        'email', 
        'user_type', 
        'is_staff', 
        'total_api_requests',
        'last_24h_requests',
        'last_hour_requests',
        'view_requests_link'
    )
    list_display_links = ('email',)
    list_filter = ('user_type', 'is_staff', 'is_superuser', 'is_active')
    search_fields = ('email', 'first_name', 'last_name')

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'user_type')}),
        ('API Usage Statistics', {
            'fields': (
                'total_api_requests_display',
                'last_24h_requests_display',
                'last_hour_requests_display',
            ),
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    readonly_fields = (
        'total_api_requests_display',
        'last_24h_requests_display',
        'last_hour_requests_display',
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
        ('Personal info', {'fields': ('first_name', 'last_name', 'user_type')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
    )

    inlines = [APIRequestInline]

    def total_api_requests(self, obj):
        count = obj.api_requests.count()
        return format_html('<b>{}</b>', count)
    total_api_requests.short_description = 'Total Requests'

    def last_24h_requests(self, obj):
        count = obj.get_recent_requests(within_minutes=1440).count()  # 24 hours = 1440 minutes
        return format_html('<b>{}</b>', count)
    last_24h_requests.short_description = 'Last 24h'

    def last_hour_requests(self, obj):
        count = obj.get_recent_requests(within_minutes=60).count()
        return format_html('<b>{}</b>', count)
    last_hour_requests.short_description = 'Last Hour'

    def view_requests_link(self, obj):
        url = reverse('admin:your_app_name_apirequest_changelist')  # Replace 'your_app_name'
        return format_html('<a href="{}?user__id__exact={}">View All Requests</a>', url, obj.id)
    view_requests_link.short_description = 'Details'

    # Read-only field displays for the detail view
    def total_api_requests_display(self, obj):
        return f"Total Requests: {obj.api_requests.count()}"
    total_api_requests_display.short_description = "Total API Requests"

    def last_24h_requests_display(self, obj):
        return f"Last 24 Hours: {obj.get_recent_requests(within_minutes=1440).count()}"
    last_24h_requests_display.short_description = "Requests (Last 24 Hours)"

    def last_hour_requests_display(self, obj):
        return f"Last Hour: {obj.get_recent_requests(within_minutes=60).count()}"
    last_hour_requests_display.short_description = "Requests (Last Hour)"


@admin.register(APIRequest)
class APIRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'timestamp', 'user_type')
    list_filter = ('user__user_type', 'timestamp')
    search_fields = ('user__email',)
    ordering = ('-timestamp',)
    
    def user_type(self, obj):
        return obj.user.user_type
    user_type.short_description = 'User Type'

    def has_add_permission(self, request):
        return False