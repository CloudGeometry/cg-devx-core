import functools
import logging

from common.logging_config import logger


def trace():
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            level = logger.getEffectiveLevel()
            try:
                args_repr = [repr(a) for a in args]
                kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]
                signature = ", ".join(args_repr + kwargs_repr)

                logger.debug(f"function {func.__qualname__}.{func.__name__} called with args {signature}")
                if level is not logging.DEBUG:
                    logger.info(f"function {func.__qualname__}.{func.__name__} called")
            except Exception:
                pass

            try:
                result = func(*args, **kwargs)
                logger.debug(f"function {func.__qualname__}.{func.__name__} returned {str(result)}")
                if level is not logging.DEBUG:
                    logger.info(f"function {func.__qualname__}.{func.__name__} exited")
                return result
            except Exception as e:
                logger.exception(f"Exception raised in {func.__name__}. exception: {str(e)}")
                raise e

        return wrapper

    return decorator
