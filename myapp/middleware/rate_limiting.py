from django.http import JsonResponse
from django.utils import timezone

class RateLimitingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.rate_limits = {
            "GOLD": 10,
            "SILVER": 5,
            "BRONZE": 2,
            "DEFAULT": 1,
        }

    def __call__(self, request):
        # Only check rate limiting for API routes
        if not request.path.startswith("/api/"):
            return self.get_response(request)

        # Check authentication
        if not request.user.is_authenticated:
            return JsonResponse({
                "error": "Unauthorized access. Please authenticate."
            }, status=401)

        # Get user's rate limit based on their type
        rate_limit = self.rate_limits.get(request.user.user_type, self.rate_limits["DEFAULT"])
        
        # Get recent requests in the last minute
        recent_requests = request.user.get_recent_requests(within_minutes=1)
        request_count = recent_requests.count()

        # If limit exceeded, return error with details
        if request_count >= rate_limit:
            newest_request = recent_requests.order_by('-timestamp').first()
            retry_after = 60 - (timezone.now() - newest_request.timestamp).seconds
            
            return JsonResponse({
                "error": "Rate limit exceeded",
                "message": f"You have made {request_count} requests in the last minute. Your limit is {rate_limit} requests per minute.",
                "user_type": request.user.user_type,
                "retry_after_seconds": max(0, retry_after),
            }, status=429)

        # Add the current request to the database
        request.user.add_api_request()
        
        # Get the response
        response = self.get_response(request)
        
        # Add rate limit headers
        response["X-RateLimit-Limit"] = str(rate_limit)
        response["X-RateLimit-Remaining"] = str(max(0, rate_limit - request_count - 1))
        response["X-RateLimit-Type"] = str(request.user.user_type)
        
        return response