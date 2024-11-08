import logging
from django.http import JsonResponse

logging.basicConfig(
    filename="rate_limiting.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger()


class ExcludeAutoreloadFilter(logging.Filter):
    def filter(self, record):
        if "django.utils.autoreload" in record.pathname:
            return False
        return True


logger.addFilter(ExcludeAutoreloadFilter())


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
        user = request.user
        rate_limit = user.get_rate_limit()
        if not user.can_make_request():
            logger.info(
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
        logger.info(
            f"User {user.email} from IP {request.META['REMOTE_ADDR']} made a request. Hit count: {user.hit_count}"
        )

        response = self.get_response(request)
        return response
