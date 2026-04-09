import time
import redis
import os
import asyncio

async def main():
    print("testing testing")
    REDIS_HOST = os.getenv("REDIS_HOST", "redis_storage")
    r = redis.Redis(host=REDIS_HOST, port=6379, db=0, decode_responses=True)
    while True:
        await asyncio.sleep(5)
        print("main")
        query_redis(r)

def query_redis(redis_object):
    print("query redis")
    tasks = redis_object.lrange("test_tasks", 0, -1)
    for task in tasks:
        print(f"Task: {task}")

if __name__ == "__main__":
    asyncio.run(main())