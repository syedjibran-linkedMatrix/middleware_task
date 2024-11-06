from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from datetime import timedelta
from django.utils import timezone
from django.db.models import Count

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    username = None
    email = models.EmailField("email address", unique=True)
    user_type = models.CharField(
        max_length=10,
        choices=[
            ("BRONZE", "Bronze"),
            ("SILVER", "Silver"),
            ("GOLD", "Gold"),
        ],
        default="BRONZE",
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def get_recent_requests(self, within_minutes=1):
        """Return requests within a specified time frame in minutes."""
        cutoff_time = timezone.now() - timedelta(minutes=within_minutes)
        return self.api_requests.filter(timestamp__gte=cutoff_time)

    def add_api_request(self):
        return APIRequest.objects.create(user=self, timestamp=timezone.now())

    def get_requests_count(self):
        return self.api_requests.count()

    def get_daily_requests_count(self):
        return self.get_recent_requests(within_minutes=1440).count()

    def get_hourly_requests_count(self):
        return self.get_recent_requests(within_minutes=60).count()

    def get_rate_limit(self):
        rate_limits = {
            "GOLD": 10,
            "SILVER": 5,
            "BRONZE": 2,
            "DEFAULT": 1
        }
        return rate_limits.get(self.user_type, 1)

    def can_make_request(self):
        return self.get_hourly_requests_count() < self.get_rate_limit()

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-date_joined']


class APIRequest(models.Model):
    user = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE, 
        related_name="api_requests"
    )
    timestamp = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['timestamp']),
            models.Index(fields=['user', 'timestamp']),
        ]
        verbose_name = 'API Request'
        verbose_name_plural = 'API Requests'

    def __str__(self):
        return f"API request by {self.user.email} at {self.timestamp}"

    @classmethod
    def get_requests_by_user_type(cls):
        """Get count of requests grouped by user type."""
        return cls.objects.values(
            'user__user_type'
        ).annotate(
            total_requests=Count('id')
        ).order_by('user__user_type')

    @classmethod
    def get_total_requests_today(cls):
        """Get total requests made today."""
        today = timezone.now().date()
        return cls.objects.filter(
            timestamp__date=today
        ).count()