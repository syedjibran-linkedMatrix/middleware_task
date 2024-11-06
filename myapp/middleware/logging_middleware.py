import logging
import os
from datetime import datetime


class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

        # Configure logging
        log_dir = "logs"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        logging.basicConfig(
            filename=os.path.join(log_dir, "requests.log"),
            level=logging.INFO,
            format="%(asctime)s - %(message)s",
        )
        self.logger = logging.getLogger("request_logger")

    def __call__(self, request):
        # Only log requests to the "/api/" path
        if request.path == "/api/":
            ip_address = request.META.get("REMOTE_ADDR")
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            path = request.path

            self.logger.info(f"IP: {ip_address} - Path: {path}")
        response = self.get_response(request)
        return response