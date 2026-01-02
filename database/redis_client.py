import redis.asyncio as redis
import os

redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")

redis_client = redis.from_url(redis_url, decode_responses=True)

async def check_redis():
    try:
        await redis_client.ping()
        print("redis is working!")
    except Exception as e:
        print(f"error Redis: {e}")
