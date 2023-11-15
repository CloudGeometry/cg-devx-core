import random
import time
from common.logging_config import logger


def exponential_backoff(max_retries: int = 5, base_delay: float = 15):
    def decorator(func):
        def wrapper(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    result_func = func(*args, **kwargs)
                    return result_func
                except Exception as e:
                    logger.info(f"Attempt {retries + 1} failed: {e}")
                    retries += 1
                    delay = (base_delay * 2 ** retries + random.uniform(0, 1))
                    logger.info(f"Retrying in {delay:.2f} seconds...")
                    time.sleep(delay)
            raise Exception("Max retries reached, operation failed.")

        return wrapper

    return decorator
