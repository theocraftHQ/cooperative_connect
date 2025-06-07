import redis

from cooperative_connect.root.settings import Settings

settings = Settings()
redis_url = str(settings.redis_url)
cc_redis = redis.Redis(decode_responses=True)
cc_redis.from_url(url=redis_url)
