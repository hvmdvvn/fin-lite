import json
import redis
from sqlalchemy import text
from jinja2 import Template

from app.db.session import SessionLocal
from app.core.tenancy import set_tenant_context
from app.agents.llm import generate_reply


redis_client = redis.Redis(
    host="127.0.0.1",
    port=6379,
    decode_responses=True,
    protocol=2,
    socket_timeout=None,
    socket_connect_timeout=10,
    health_check_interval=30,
)

PROMPT_PATH = "app/agents/prompts/classifier_v1.txt"

VALID_CATEGORIES = {"billing", "bug", "how_to", "other"}
VALID_URGENCY = {"low", "normal", "high"}


def load_prompt():
    with open(PROMPT_PATH, "r", encoding="utf-8") as f:
        return f.read()


def process_job(job: dict):
    db = SessionLocal()

    try:
        tenant_id = job["tenant_id"]
        ticket_id = job["ticket_id"]

        # ---------------------------
        # 1. Set tenant context (RLS)
        # ---------------------------
        set_tenant_context(db, tenant_id)

        # ---------------------------
        # 2. Load ticket
        # ---------------------------
        ticket = db.execute(
            text("""
                SELECT subject, body
                FROM tickets
                WHERE id = :id
            """),
            {"id": ticket_id},
        ).mappings().first()

        if not ticket:
            print("Ticket not found")
            return

        # ---------------------------
        # 3. Build prompt
        # ---------------------------
        template = load_prompt()

        prompt = Template(template).render(
            subject=ticket["subject"],
            body=ticket["body"],
        )

        # ---------------------------
        # 4. Call LLM (cheap/fast model)
        # ---------------------------
        response = generate_reply(prompt)

        try:
            result = json.loads(response)
            category = result["category"]
            urgency = result["urgency"]

            if category not in VALID_CATEGORIES or urgency not in VALID_URGENCY:
                raise ValueError(f"invalid category/urgency: {result}")

        except Exception as e:
            print(f"Classifier parse failed for {ticket_id}: {e}. Falling back to defaults.")
            category, urgency = "other", "normal"

        # ---------------------------
        # 5. Save classification
        # ---------------------------
        db.execute(
            text("""
                UPDATE tickets
                SET category = :category,
                    status = 'classified'
                WHERE id = :ticket_id
            """),
            {
                "ticket_id": ticket_id,
                "category": category,
            },
        )

        db.commit()

        print(f"Ticket {ticket_id} classified as {category}/{urgency}")

        # ---------------------------
        # 6. Enqueue retrieve stage
        # ---------------------------
        redis_client.lpush(
            "retrieve",
            json.dumps(
                {
                    "ticket_id": ticket_id,
                    "tenant_id": tenant_id,
                    "category": category,
                    "urgency": urgency,
                }
            ),
        )

    except Exception as e:
        db.rollback()
        print(f"Classifier worker error on job {job}: {e}")

    finally:
        db.close()


def worker():
    print("Classifier worker started...")

    while True:
        item = redis_client.brpop("classify", timeout=5)

        if item is None:
            continue

        _, payload = item

        try:
            job = json.loads(payload)
        except json.JSONDecodeError:
            print(f"Bad job payload: {payload}")
            continue

        process_job(job)


if __name__ == "__main__":
    worker()