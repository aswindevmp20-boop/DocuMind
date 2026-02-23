import redis
import os
import json

redis_client = redis.Redis.from_url(os.getenv("REDIS_URL"))

def enqueue_query(query_id: int):
    redis_client.rpush("query_queue", json.dumps({"query_id": query_id}))

def dequeue_query():
    _,data = redis_client.blpop("query_queue")
    return json.loads(data)