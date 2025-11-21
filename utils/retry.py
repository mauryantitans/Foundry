import time
import functools
from google.api_core import exceptions

def retry_with_backoff(retries=5, initial_delay=1, backoff_factor=2):
    """
    Decorator to retry a function with exponential backoff.
    Catches Google API ResourceExhausted (429) errors.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            delay = initial_delay
            for i in range(retries):
                try:
                    return func(*args, **kwargs)
                except exceptions.ResourceExhausted as e:
                    if i == retries - 1:
                        print(f"   ❌ Max retries exceeded for {func.__name__}.")
                        raise e
                    
                    print(f"   ⏳ Rate limit hit. Retrying in {delay}s... (Attempt {i+1}/{retries})")
                    time.sleep(delay)
                    delay *= backoff_factor
                except Exception as e:
                    # For other errors, re-raise immediately
                    raise e
            return None
        return wrapper
    return decorator
