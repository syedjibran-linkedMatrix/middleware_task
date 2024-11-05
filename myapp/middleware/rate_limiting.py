from django.core.cache import cache
from django.http import HttpResponseForbidden
from datetime import datetime

class RateLimitingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.cache_timeout = 60  # 1 minute

    def __call__(self, request):
        # Apply rate limiting for the /api/ endpoint only
        if request.path == '/api/':
            ip_address = request.META.get('REMOTE_ADDR')
            cache_key = f'rate_limit_{ip_address}'
            requests = cache.get(cache_key, [])

            # Remove requests older than 1 minute
            now = datetime.now()
            requests = [req for req in requests 
                        if (now - req).total_seconds() < self.cache_timeout]

            # Determine rate limit based on authentication
            if request.user.is_authenticated:
                # Determine the user's rate limit based on their user type
                if request.user.user_type == 'GOLD':
                    rate_limit = 10  # Gold users: 10 requests per minute
                elif request.user.user_type == 'SILVER':
                    rate_limit = 5   # Silver users: 5 requests per minute
                elif request.user.user_type == 'BRONZE':
                    rate_limit = 2   # Bronze users: 2 requests per minute
            else:
                rate_limit = 1  # Unauthenticated users: 1 request per minute

            # Check if the request count exceeds the limit
            if len(requests) >= rate_limit:
                return HttpResponseForbidden('Rate limit exceeded. Please try again later.')

            requests.append(now)
            cache.set(cache_key, requests, self.cache_timeout)

        # Always allow access to other paths
        return self.get_response(request)
