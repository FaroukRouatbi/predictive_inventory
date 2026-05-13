from slowapi import Limiter
from slowapi.util import get_remote_address
import os

# Disable rate limiting when RATELIMIT_ENABLED=0 (used in tests)
enabled = os.environ.get("RATELIMIT_ENABLED", "1") != "0"

limiter = Limiter(key_func=get_remote_address, enabled=enabled)