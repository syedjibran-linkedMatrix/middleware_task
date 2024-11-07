import logging
from django.http import JsonResponse
from myapp.models import CustomUser

logging.basicConfig(
    filename="rate_limiting.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


class RateLimitingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.path.startswith("/api/"):
            return self.get_response(request)

        if not request.user.is_authenticated:
            return JsonResponse(
                {"error": "Unauthorized access. Please authenticate."}, status=401
            )

        if not isinstance(request.user, CustomUser):
            return JsonResponse({"error": "Invalid user type"}, status=400)

        user = request.user
        rate_limit = user.get_rate_limit()

        if not user.can_make_request():
            logging.info(
                f"User {user.email} from IP {request.META['REMOTE_ADDR']} has hit the rate limit. Hit count: {user.hit_count}"
            )
            return JsonResponse(
                {
                    "error": "Rate limit exceeded",
                    "message": f"You have made {user.hit_count} requests in the last minute. Your limit is {rate_limit} requests per minute. Please try again later.",
                },
                status=429,
            )

        user.increment_hit_count()
        logging.info(
            f"User {user.email} from IP {request.META['REMOTE_ADDR']} made a request. Hit count: {user.hit_count}"
        )

        response = self.get_response(request)
        response["X-RateLimit-Limit"] = str(rate_limit)
        response["X-RateLimit-Remaining"] = str(rate_limit - user.hit_count)
        response["X-RateLimit-Type"] = str(user.user_type)

        return response
