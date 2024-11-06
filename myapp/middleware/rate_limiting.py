from django.http import JsonResponse
from django.utils import timezone

class RateLimitingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Only check rate limiting for API routes
        if not request.path.startswith("/api/"):
            return self.get_response(request)

        # Check authentication
        if not request.user.is_authenticated:
            return JsonResponse({
                "error": "Unauthorized access. Please authenticate."
            }, status=401)

        # Get the user's rate limit based on their user type
        user = request.user
        rate_limit = user.get_rate_limit()

        # Check if the user can make a request based on their rate limit
        if not user.can_make_request():
            # If the limit is exceeded, return an error response
            retry_after = 60 - (timezone.now() - user.last_hit_time).seconds
            return JsonResponse({
                "error": "Rate limit exceeded",
                "message": f"You have made {user.hit_count} requests in the last minute. Your limit is {rate_limit} requests per minute.",
                "retry_after_seconds": max(0, retry_after),
            }, status=429)

        # Increment the hit count for the user
        user.increment_hit_count()

        # Proceed with the request and get the response
        response = self.get_response(request)

        # Add rate limit headers to the response
        response["X-RateLimit-Limit"] = str(rate_limit)
        response["X-RateLimit-Remaining"] = str(rate_limit - user.hit_count)
        response["X-RateLimit-Type"] = str(user.user_type)

        return response
