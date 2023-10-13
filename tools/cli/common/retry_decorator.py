import random
import time


def exponential_backoff_decorator(max_retries: int = 5, base_delay: float = 15):
    def decorator(func):
        def wrapper(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    result_func = func(*args, **kwargs)
                    return result_func
                except Exception as e:
                    print(f"Attempt {retries + 1} failed: {e}")
                    retries += 1
                    delay = (base_delay * 2 ** retries + random.uniform(0, 1))
                    print(f"Retrying in {delay:.2f} seconds...")
                    time.sleep(delay)
            raise Exception("Max retries reached, operation failed.")

        return wrapper

    return decorator
