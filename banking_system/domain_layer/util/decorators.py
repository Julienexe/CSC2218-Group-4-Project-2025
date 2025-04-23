from functools import wraps

def validate_transaction(action):
    def decorator(func):
        @wraps(func)
        def wrapper(self, amount, *args, **kwargs):
            if not self.is_active():
                raise ValueError(f"Cannot {action} from a closed account.")

            if amount <= 0:
                raise ValueError(f"{action} amount must be positive.")

            if hasattr(self, 'balance') and amount > self.balance:
                raise ValueError(f"Insufficient funds for {action}.")

            return func(self, amount, *args, **kwargs)
        return wrapper
    return decorator