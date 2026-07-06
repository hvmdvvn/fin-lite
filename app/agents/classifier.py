import json
from app.core.queue import get_next_classify_job, enqueue_retrieve

print("🔥 CLASSIFIER WORKER STARTED")

while True:
    job = get_next_classify_job()

    if job is None:
        continue

    _, payload = job

    try:
        data = json.loads(payload)
    except json.JSONDecodeError:
        print("❌ Bad job:", payload)
        continue

    ticket_id = data["ticket_id"]
    tenant_id = data["tenant_id"]

    print("📥 Received job:", ticket_id)

    category = "general"

    print("🏷 Classified as:", category)

    enqueue_retrieve(ticket_id, tenant_id)