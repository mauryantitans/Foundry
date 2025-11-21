import time
import threading
from utils.config import TierConfig

class RateLimiter:
    def __init__(self, config: TierConfig):
        self.config = config
        self.rate = config.requests_per_minute / 60.0  # Requests per second
        self.tokens = 1.0 # Start with 1 token
        self.last_update = time.time()
        self.lock = threading.Lock()
        
        print(f"🚦 Rate Limiter initialized for {config.name} tier ({config.requests_per_minute} RPM)")

    def wait_for_token(self):
        """Blocks until a token is available."""
        with self.lock:
            while True:
                now = time.time()
                elapsed = now - self.last_update
                
                # Refill tokens
                self.tokens += elapsed * self.rate
                if self.tokens > 1.0:
                    self.tokens = 1.0 # Cap at 1 (strict spacing)
                
                self.last_update = now
                
                if self.tokens >= 1.0:
                    self.tokens -= 1.0
                    return
                
                # Calculate wait time
                wait_time = (1.0 - self.tokens) / self.rate
                if wait_time > 0:
                    time.sleep(wait_time)
