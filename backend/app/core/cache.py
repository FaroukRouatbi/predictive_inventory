import redis
import json
from app.config import settings

r = redis.Redis.from_url(settings.REDIS_URL) 


def get_cached_forecast(key: str) -> dict | None:
    value = r.get(key)
    if value:
        return json.loads(value)
    return None


def set_cached_forecast(key: str, data: dict, ttl: int = 300) -> None:
    r.setex(key, ttl, json.dumps(data))


def build_forecast_key(product_id: str, horizon_days: int, history_days: int) -> str:
    return f"forecast:{product_id}:{horizon_days}:{history_days}"