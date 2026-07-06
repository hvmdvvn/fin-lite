import redis
import json

# redis_client = redis.Redis(host="localhost", port=6379, decode_responses=True)

redis_client = redis.Redis(
    host="127.0.0.1",
    port=6379,
    decode_responses=True,
    protocol=2,  # 🔥 THIS IS THE KEY FIX
    socket_timeout=None,
    socket_connect_timeout=10,
    health_check_interval=30,
)


QUEUE_CLASSIFY = "classify"
QUEUE_RETRIEVE = "retrieve"


def enqueue_classify(ticket_id: str, tenant_id: str):
    redis_client.lpush(
        QUEUE_CLASSIFY,
        json.dumps({
            "ticket_id": ticket_id,
            "tenant_id": tenant_id
        })
    )

def enqueue_retrieve(ticket_id: str, tenant_id: str):
    redis_client.lpush(
        QUEUE_RETRIEVE,
        json.dumps({
            "ticket_id": ticket_id,
            "tenant_id": tenant_id
        })
    )


def get_next_classify_job():
    return redis_client.brpop(QUEUE_CLASSIFY, timeout=5)