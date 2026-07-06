import json
import redis
from sqlalchemy import text
from jinja2 import Template

from app.db.session import SessionLocal
from app.core.tenancy import set_tenant_context
from app.agents.llm import generate_reply


# redis_client = redis.Redis(
#     host="localhost",
#     port=6379,
#     decode_responses=True,
#     socket_timeout=None,          # IMPORTANT
#     socket_connect_timeout=10,
# )

redis_client = redis.Redis(
    host="127.0.0.1",
    port=6379,
    decode_responses=True,
    protocol=2,  # 🔥 THIS IS THE KEY FIX
    socket_timeout=None,
    socket_connect_timeout=10,
    health_check_interval=30,
)

PROMPT_PATH = "app/agents/prompts/drafter_v1.txt"


def load_prompt():
    with open(PROMPT_PATH, "r", encoding="utf-8") as f:
        return f.read()


def fetch_kb_articles(db, chunk_ids):
    if not chunk_ids:
        return []

    rows = db.execute(
        text("""
            SELECT id, title, body
            FROM kb_articles
            WHERE id = ANY(CAST(:ids AS uuid[]))
        """),
        {
            "ids": chunk_ids
        },
    ).mappings().all()

    return rows


def process_job(job: dict):
    db = SessionLocal()

    try:
        tenant_id = job["tenant_id"]
        ticket_id = job["ticket_id"]
        chunk_ids = job.get("chunk_ids", [])

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
        # 3. Load KB articles
        # ---------------------------
        kb_articles = fetch_kb_articles(db, chunk_ids)

        kb_text = "\n\n".join(
            f"Title: {kb['title']}\n{kb['body']}"
            for kb in kb_articles
        )

        if not kb_articles:
            kb_text = "No relevant knowledge base articles found."

        # ---------------------------
        # 4. Build prompt
        # ---------------------------
        template = load_prompt()

        prompt = Template(template).render(
            subject=ticket["subject"],
            body=ticket["body"],
            kb=kb_text,
        )

        # ---------------------------
        # 5. Call Groq LLM
        # ---------------------------
        response = generate_reply(prompt)

        try:
            result = json.loads(response)
        except Exception:
            result = {
                "draft": response,
                "used_chunk_ids": chunk_ids,
            }

        # ---------------------------
        # 6. Save reply
        # ---------------------------
        db.execute(
            text("""
                INSERT INTO replies (
                    tenant_id,
                    ticket_id,
                    draft,
                    sent,
                    prompt_version
                )
                VALUES (
                    current_setting('app.tenant_id')::uuid,
                    :ticket_id,
                    :draft,
                    false,
                    'drafter-v1'
                )
            """),
            {
                "ticket_id": ticket_id,
                "draft": result["draft"],
            },
        )

        db.commit()

        print(f"Draft created for ticket {ticket_id}")

        # ---------------------------
        # 7. Enqueue QA (stub)
        # ---------------------------
        redis_client.lpush(
            "qa",
            json.dumps(
                {
                    "ticket_id": ticket_id,
                    "tenant_id": tenant_id,
                }
            ),
        )

    finally:
        db.close()


def worker():
    print("Drafter worker started...")

    while True:
        item = redis_client.brpop("draft", timeout=5)

        if item is None:
            continue

        _, payload = item
        job = json.loads(payload)

        process_job(job)


if __name__ == "__main__":
    worker()