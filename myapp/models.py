from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils import timezone
from datetime import timedelta


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

    hit_count = models.PositiveIntegerField(default=0)
    last_hit_time = models.DateTimeField(null=True, default=timezone.now)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def get_rate_limit(self):
        rate_limits = {"GOLD": 10, "SILVER": 5, "BRONZE": 2, "DEFAULT": 1}
        return rate_limits.get(self.user_type, rate_limits["DEFAULT"])

    def can_make_request(self):
        now = timezone.now()
        if now - self.last_hit_time > timedelta(minutes=1):
            self.hit_count = 0
            self.last_hit_time = now
        return self.hit_count < self.get_rate_limit()

    def increment_hit_count(self):
        now = timezone.now()
        if now - self.last_hit_time > timedelta(minutes=1):
            self.hit_count = 0
            self.last_hit_time = now

        self.hit_count += 1
        self.save(update_fields=["hit_count", "last_hit_time"])


    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ["-date_joined"]
