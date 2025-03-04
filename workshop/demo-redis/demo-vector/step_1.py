import os
import redis

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = os.getenv("REDIS_PORT", "6379")

# If SSL is enabled on the endpoint, use rediss:// as the URL prefix
REDIS_URL = f"redis://:{REDIS_HOST}:{REDIS_PORT}"
INDEX_NAME = f"qna:idx"


redis = redis.Redis(
  host=REDIS_HOST,
  port=REDIS_PORT
)

print(redis.ping())

