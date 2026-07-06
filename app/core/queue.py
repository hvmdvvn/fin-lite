import redis

redis_client = redis.Redis(host="localhost", port=6379, decode_responses=True)


QUEUE_CLASSIFY = "classify"


def enqueue_classify(ticket_id: str):
    redis_client.lpush(QUEUE_CLASSIFY, ticket_id)


def get_next_classify_job():
    return redis_client.brpop(QUEUE_CLASSIFY, timeout=5)