import functools

from modules.loggers import LoggerSingleton

# Decorator for error handling (Decorator Pattern)
def handle_firestore_errors(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger = LoggerSingleton.get_instance()
        try:
            return func(*args, **kwargs)
        except Exception as e:
            operation = func.__name__
            logger.error(f"Error in {operation}: {e}")
            if operation.startswith("read") or operation.startswith("get"):
                return None if "document" in operation else []
            return False
    return wrapper