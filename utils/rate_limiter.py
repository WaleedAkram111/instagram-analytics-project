"""Rate limiting utilities for API calls"""
import time
import random
from functools import wraps
from typing import Callable
from config.settings import settings
from utils.logger import get_logger

logger = get_logger(__name__)

class RateLimiter:
    def __init__(self, min_delay: float = None, max_delay: float = None):
        self.min_delay = min_delay or settings.RATE_LIMIT_MIN
        self.max_delay = max_delay or settings.RATE_LIMIT_MAX
        self.last_request = 0
        self.request_count = 0
        self.hour_start = time.time()
    
    def wait(self):
        """Wait with random delay and check hourly limits"""
        current_time = time.time()
        
        # Reset hourly counter
        if current_time - self.hour_start > 3600:
            self.request_count = 0
            self.hour_start = current_time
            logger.info("Hourly rate limit counter reset")
        
        # Check hourly limit
        if self.request_count >= settings.MAX_API_CALLS_PER_HOUR:
            wait_time = 3600 - (current_time - self.hour_start)
            logger.warning(f"Hourly rate limit reached. Waiting {wait_time:.0f} seconds...")
            time.sleep(wait_time)
            self.request_count = 0
            self.hour_start = time.time()
        
        # Calculate delay since last request
        elapsed = current_time - self.last_request
        delay = random.uniform(self.min_delay, self.max_delay)
        
        if elapsed < delay:
            sleep_time = delay - elapsed
            time.sleep(sleep_time)
        
        self.last_request = time.time()
        self.request_count += 1

def rate_limited(min_delay: float = None, max_delay: float = None):
    """Decorator for rate limiting functions"""
    limiter = RateLimiter(min_delay, max_delay)
    
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            limiter.wait()
            return func(*args, **kwargs)
        return wrapper
    return decorator