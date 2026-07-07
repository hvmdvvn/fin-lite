import json
import redis

redis_client = redis.Redis(
    host="127.0.0.1",
    port=6379,
    decode_responses=True,
    protocol=2,
    socket_timeout=None,
    socket_connect_timeout=10,
    health_check_interval=30,
)

# Queue names
QUEUE_CLASSIFY = "classify"
QUEUE_RETRIEVE = "retrieve"
QUEUE_DRAFT = "draft"
QUEUE_QA = "qa"
QUEUE_REEMBED = "reembed"


# -------------------------
# Generic helpers
# -------------------------

def enqueue(queue_name: str, payload: dict):
    redis_client.lpush(
        queue_name,
        json.dumps(payload)
    )


def dequeue(queue_name: str):
    job = redis_client.brpop(queue_name, timeout=5)

    if not job:
        return None

    return json.loads(job[1])


# -------------------------
# Classifier
# -------------------------

def enqueue_classify(ticket_id: str, tenant_id: str):
    enqueue(
        QUEUE_CLASSIFY,
        {
            "ticket_id": ticket_id,
            "tenant_id": tenant_id,
        },
    )


def get_next_classify_job():
    return dequeue(QUEUE_CLASSIFY)


# -------------------------
# Retriever
# -------------------------

def enqueue_retrieve(ticket_id: str, tenant_id: str):
    enqueue(
        QUEUE_RETRIEVE,
        {
            "ticket_id": ticket_id,
            "tenant_id": tenant_id,
        },
    )


def get_next_retrieve_job():
    return dequeue(QUEUE_RETRIEVE)


# -------------------------
# Drafter
# -------------------------

def enqueue_draft(ticket_id: str, tenant_id: str):
    enqueue(
        QUEUE_DRAFT,
        {
            "ticket_id": ticket_id,
            "tenant_id": tenant_id,
        },
    )


def get_next_draft_job():
    return dequeue(QUEUE_DRAFT)


# -------------------------
# QA
# -------------------------

def enqueue_qa(ticket_id: str, tenant_id: str):
    enqueue(
        QUEUE_QA,
        {
            "ticket_id": ticket_id,
            "tenant_id": tenant_id,
        },
    )


def get_next_qa_job():
    return dequeue(QUEUE_QA)


# -------------------------
# Re-embed
# -------------------------

def enqueue_reembed(ticket_id, tenant_id, correction):

    redis_client.lpush(
        "reembed",
        json.dumps({
            "ticket_id": ticket_id,
            "tenant_id": tenant_id,
            "correction": correction
        })
    )


def get_next_reembed_job():
    return dequeue(QUEUE_REEMBED)