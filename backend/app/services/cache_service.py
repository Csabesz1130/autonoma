from functools import wraps
from redis import Redis
import json
from app.core.config import settings

redis_client = Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)

def cache_result(expire_time=3600):
    def decorator(f):
        @wraps(f)
        async def decorated_function(*args, **kwargs):
            key = f.__name__ + str(args) + str(kwargs)
            result = redis_client.get(key)
            if result:
                return json.loads(result)
            result = await f(*args, **kwargs)
            redis_client.setex(key, expire_time, json.dumps(result))
            return result
        return decorated_function
    return decorator

class CacheService:
    @staticmethod
    def set(key: str, value: str, expire_time: int = 3600):
        redis_client.setex(key, expire_time, value)

    @staticmethod
    def get(key: str) -> str:
        return redis_client.get(key)

    @staticmethod
    def delete(key: str):
        redis_client.delete(key)

cache_service = CacheService()