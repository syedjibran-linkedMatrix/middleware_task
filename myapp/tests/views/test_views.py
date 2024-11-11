from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
import json

User = get_user_model()

class BaseViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_data = {
            "email": "test@example.com",
            "password": "testpass123",
            "user_type": "BRONZE"
        }
        self.user = User.objects.create_user(
            email=self.user_data["email"],
            password=self.user_data["password"],
            user_type=self.user_data["user_type"]
        )

class RegisterViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.register_url = reverse('register')
        self.user_data = {
            "email": "newuser@example.com",
            "password": "testpass123",
            "user_type": "BRONZE"
        }

    def test_get_register_page(self):
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'myapp/register.html')

    def test_successful_registration(self):
        response = self.client.post(self.register_url, self.user_data)
        self.assertRedirects(response, reverse('login'))
        self.assertTrue(
            User.objects.filter(email=self.user_data["email"]).exists()
        )

    def test_registration_missing_fields(self):
        response = self.client.post(self.register_url, {
            "password": "testpass123",
            "user_type": "BRONZE"
        })
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(
            str(response.content, encoding='utf8'),
            {"error": "Email and password are required"}
        )

    def test_registration_invalid_user_type(self):
        invalid_data = self.user_data.copy()
        invalid_data["user_type"] = "INVALID"
        response = self.client.post(self.register_url, invalid_data)
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(
            str(response.content, encoding='utf8'),
            {"error": "Invalid user type"}
        )

    def test_registration_duplicate_email(self):
        # Create first user
        self.client.post(self.register_url, self.user_data)
        # Try to create second user with same email
        response = self.client.post(self.register_url, self.user_data)
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(
            str(response.content, encoding='utf8'),
            {"error": "User with this email already exists"}
        )

class LoginViewTest(BaseViewTest):
    def setUp(self):
        super().setUp()
        self.login_url = reverse('login')

    def test_get_login_page(self):
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'myapp/login.html')

    def test_successful_login(self):
        response = self.client.post(self.login_url, {
            "email": self.user_data["email"],
            "password": self.user_data["password"]
        })
        self.assertRedirects(response, reverse('home'))

    def test_login_missing_fields(self):
        response = self.client.post(self.login_url, {
            "email": self.user_data["email"]
        })
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(
            str(response.content, encoding='utf8'),
            {"error": "Email and password are required"}
        )

    def test_login_invalid_credentials(self):
        response = self.client.post(self.login_url, {
            "email": self.user_data["email"],
            "password": "wrongpassword"
        })
        self.assertEqual(response.status_code, 401)
        self.assertJSONEqual(
            str(response.content, encoding='utf8'),
            {"error": "Invalid credentials"}
        )

    def test_login_user_not_found(self):
        response = self.client.post(self.login_url, {
            "email": "nonexistent@example.com",
            "password": "testpass123"
        })
        self.assertEqual(response.status_code, 404)
        self.assertJSONEqual(
            str(response.content, encoding='utf8'),
            {"error": "User not found"}
        )

class LogoutViewTest(BaseViewTest):
    def setUp(self):
        super().setUp()
        self.logout_url = reverse('logout')

    def test_logout_authenticated_user(self):
        self.client.login(
            email=self.user_data["email"],
            password=self.user_data["password"]
        )
        response = self.client.post(self.logout_url)
        self.assertRedirects(response, reverse('login'))

    def test_logout_unauthenticated_user(self):
        response = self.client.post(self.logout_url)
        self.assertRedirects(response, reverse('home'))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), "You are not logged in.")

class ApiViewTest(BaseViewTest):
    def setUp(self):
        super().setUp()
        self.api_url = reverse('api')

    def test_api_unauthenticated(self):
        response = self.client.get(self.api_url)
        self.assertEqual(response.status_code, 401)
        self.assertJSONEqual(
            str(response.content, encoding='utf8'),
            {"error": "Unauthorized access. Please authenticate."}
        )

    def test_api_authenticated(self):
        self.client.login(
            email=self.user_data["email"],
            password=self.user_data["password"]
        )
        response = self.client.get(self.api_url)
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEqual(content["status"], "success")
        self.assertEqual(content["user"]["email"], self.user_data["email"])
        self.assertEqual(content["user"]["type"], self.user_data["user_type"])
        self.assertIn("rate_limiting", content)

class FreeViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.free_url = reverse('free')

    def test_free_endpoint(self):
        response = self.client.get(self.free_url)
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            str(response.content, encoding='utf8'),
            {"message": "This is a free endpoint"}
        )

class HomeViewTest(BaseViewTest):
    def setUp(self):
        super().setUp()
        self.home_url = reverse('home')

    def test_home_page_load(self):
        response = self.client.get(self.home_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'myapp/home.html')

    def test_home_page_authenticated(self):
        self.client.login(
            email=self.user_data["email"],
            password=self.user_data["password"]
        )
        response = self.client.get(self.home_url)
        self.assertEqual(response.status_code, 200)