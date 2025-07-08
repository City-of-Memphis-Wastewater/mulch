from functools import wraps
from pathlib import Path
from mulch.logging_setup import setup_logging, setup_logging_portable

def with_logging(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Prefer explicit target_dir, fallback to cwd
        target_dir = kwargs.get("target_dir", Path.cwd())
        setup_logging_portable()
        #setup_logging(target_dir)
        return func(*args, **kwargs)
    return wrapper
