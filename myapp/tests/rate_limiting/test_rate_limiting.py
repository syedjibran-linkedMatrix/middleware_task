# tests/middleware/test_rate_limiting.py
import logging
import json
from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from unittest.mock import patch, MagicMock
from myapp.middleware.rate_limiting import RateLimitingMiddleware
from django.contrib.auth import get_user_model

User = get_user_model()

class RateLimitingMiddlewareTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpass123",
            user_type="BRONZE"
        )
        
        self.user.get_rate_limit = MagicMock(return_value=5)
        self.user.can_make_request = MagicMock()
        self.user.increment_hit_count = MagicMock()

        # Mocking the get_response callable
        self.get_response = MagicMock(return_value=self.mock_success_response())
        self.middleware = RateLimitingMiddleware(self.get_response)

    def mock_success_response(self):
        response = MagicMock()
        response.status_code = 200
        response.content = json.dumps({"message": "Success"})  
        return response

    @patch.object(logging.getLoggerClass(), "info")
    def test_unauthenticated_user_access(self, mock_logger):
        request = self.factory.get("/api/")
        request.user = MagicMock(is_authenticated=False)
        
        response = self.middleware.__call__(request) 

        self.assertEqual(response.status_code, 401)
        # Directly check the content of the response
        self.assertEqual(json.loads(response.content), {"error": "Unauthorized access. Please authenticate."})
        mock_logger.assert_not_called()

    @patch.object(logging.getLoggerClass(), "info")
    def test_authenticated_user_within_rate_limit(self, mock_logger):
        request = self.factory.get("/api/")
        request.user = self.user
        self.user.can_make_request.return_value = True  
        
        response = self.middleware.__call__(request)  

        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), {"message": "Success"})
        self.user.increment_hit_count.assert_called_once()
        mock_logger.assert_called_once_with(
            f"User {self.user.email} from IP {request.META.get('REMOTE_ADDR')} made a request. Hit count: {self.user.hit_count}"
        )

    @patch.object(logging.getLoggerClass(), "info")
    def test_authenticated_user_exceeds_rate_limit(self, mock_logger):
        request = self.factory.get("/api/")
        request.user = self.user
        self.user.can_make_request.return_value = False 
        
        response = self.middleware.__call__(request)  

        self.assertEqual(response.status_code, 429)
        self.assertEqual(json.loads(response.content), {
            "error": "Rate limit exceeded",
            "message": f"You have made {self.user.hit_count} requests in the last minute. Your limit is {self.user.get_rate_limit()} requests per minute. Please try again later."
        })
        self.user.increment_hit_count.assert_not_called()
        mock_logger.assert_called_once_with(
            f"User {self.user.email} from IP {request.META.get('REMOTE_ADDR')} has hit the rate limit. Hit count: {self.user.hit_count}"
        )

    def test_non_api_request_bypasses_middleware(self):
        request = self.factory.get("/non-api/")
        request.user = MagicMock(is_authenticated=True)
        
        response = self.middleware.__call__(request)  

        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), {"message": "Success"})
