from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


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

    def get_rate_limit(self):
        limits = {"GOLD": 10, "SILVER": 5, "BRONZE": 2, None: 1}
        return limits.get(self.user_type, 1)
