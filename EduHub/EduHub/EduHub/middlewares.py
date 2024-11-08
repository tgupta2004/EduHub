from django.core.cache import cache
from django.shortcuts import render
import time
import logging

logger = logging.getLogger(__name__)

class DDoSProtectionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.rate_limit = 100  # Maximum number of POST requests allowed
        self.time_window = 60  # Time window in seconds (2 minutes)

    def __call__(self, request):
        # Only apply the middleware to POST requests
        if request.method == 'POST':
            ip_address = self.get_client_ip(request)
            cache_key_count = f"rate_limit_{ip_address}_count"
            cache_key_time = f"rate_limit_{ip_address}_time"

            # Get the current request count and the last timestamp from cache
            request_count = cache.get(cache_key_count, 0)
            last_request_time = cache.get(cache_key_time, time.time())
            current_time = time.time()

            # Debug logs for tracking
            logger.debug(f"IP: {ip_address}, Request Count: {request_count}, Last Request Time: {last_request_time}")

            # Check if the time window has passed
            if current_time - last_request_time > self.time_window:
                # Reset the count if time window is exceeded
                logger.debug(f"Time window exceeded for {ip_address}. Resetting request count.")
                request_count = 0
                last_request_time = current_time
                cache.set(cache_key_time, current_time, timeout=self.time_window)

            # If the request count exceeds the limit, block the request
            if request_count >= self.rate_limit:
                logger.debug(f"Rate limit exceeded for {ip_address}. Blocking request.")
                return render(request, 'rate_limited.html', status=429)

            # Increment request count and update cache with current time
            cache.set(cache_key_count, request_count + 1, timeout=self.time_window)
            cache.set(cache_key_time, current_time, timeout=self.time_window)
            logger.debug(f"New request count for {ip_address}: {request_count + 1}")

        # Proceed with the normal request flow for non-POST requests
        response = self.get_response(request)
        return response

    def get_client_ip(self, request):
        """Extract the client's IP address from the request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
