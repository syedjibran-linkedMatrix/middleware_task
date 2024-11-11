from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

class CustomUserManagerTests(TestCase):
    def setUp(self):
        self.user_data = {
            "email": "test@example.com",
            "password": "testpass123",
        }

    def test_create_user(self):
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(user.email, self.user_data["email"])
        self.assertTrue(user.check_password(self.user_data["password"]))
        self.assertFalse(user.is_superuser)
        self.assertFalse(user.is_staff)
        self.assertEqual(user.user_type, "BRONZE")

    def test_create_user_without_email(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(email="", password="testpass123")

    def test_create_superuser(self):
        superuser = User.objects.create_superuser(**self.user_data)
        self.assertEqual(superuser.email, self.user_data["email"])
        self.assertTrue(superuser.check_password(self.user_data["password"]))
        self.assertTrue(superuser.is_superuser)
        self.assertTrue(superuser.is_staff)

    def test_email_normalization(self):
        email = "Test@EXAMPLE.com"
        user = User.objects.create_user(email=email, password="testpass123")
        self.assertEqual(user.email, "Test@example.com")

class CustomUserTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpass123",
        )

    def test_user_type_choices(self):
        self.assertEqual(self.user.user_type, "BRONZE")
        
        # Test changing user type
        self.user.user_type = "SILVER"
        self.user.save()
        self.assertEqual(self.user.user_type, "SILVER")

    def test_get_rate_limit(self):
        rate_limits = {
            "BRONZE": 2,
            "SILVER": 5,
            "GOLD": 10,
        }
        
        for user_type, expected_limit in rate_limits.items():
            self.user.user_type = user_type
            self.assertEqual(self.user.get_rate_limit(), expected_limit)

    def test_can_make_request(self):
        self.assertTrue(self.user.can_make_request())
        
        self.user.increment_hit_count()
        self.assertTrue(self.user.can_make_request())
        
        self.user.increment_hit_count()
        self.assertFalse(self.user.can_make_request())

    def test_hit_count_reset(self):
        self.user.increment_hit_count()
        self.user.increment_hit_count()
        self.assertEqual(self.user.hit_count, 2)
        
        self.user.last_hit_time = timezone.now() - timedelta(minutes=2)
        self.user.save()
        
        self.user.increment_hit_count()
        self.assertEqual(self.user.hit_count, 1)

    def test_different_user_type_rate_limits(self):
        test_cases = [
            ("BRONZE", 2),
            ("SILVER", 5),
            ("GOLD", 10),
        ]
        
        for user_type, max_requests in test_cases:
            self.user.user_type = user_type
            self.user.hit_count = 0
            self.user.save()
            
            # Make requests up to the limit
            for _ in range(max_requests):
                self.assertTrue(self.user.can_make_request())
                self.user.increment_hit_count()
            
            # Next request should be denied
            self.assertFalse(self.user.can_make_request())

    def test_unicode_email(self):
        user = User.objects.create_user(
            email="test@例子.com",
            password="testpass123"
        )
        self.assertEqual(user.email, "test@例子.com")

    def test_email_uniqueness(self):
        with self.assertRaises(Exception): 
            User.objects.create_user(
                email="test@example.com",
                password="different_password"
            )

    def test_ordering(self):
        user1 = User.objects.create_user(
            email="user1@example.com",
            password="testpass123"
        )
        user2 = User.objects.create_user(
            email="user2@example.com",
            password="testpass123"
        )
        
        # Get ordered users
        users = User.objects.all()
        
        self.assertEqual(users[0], user2)  
        self.assertEqual(users[1], user1)  