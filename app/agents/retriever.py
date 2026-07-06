import json
import redis

from sqlalchemy import text

from app.db.session import SessionLocal
from app.rag.embed import embed_text
from app.core.tenancy import set_tenant_context


# redis_client = redis.Redis(
#     host="localhost",
#     port=6379,
#     decode_responses=True,
#     protocol=2,
#     socket_timeout=None,
#     socket_connect_timeout=5,
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


TOP_K = 5


def process_job(job: dict):
    """
    Process one retrieval job.
    Expected payload:
    {
        "ticket_id": "...",
        "tenant_id": "..."
    }
    """

    db = SessionLocal()

    try:
        tenant_id = job["tenant_id"]

        # Set PostgreSQL tenant context (RLS)
        set_tenant_context(db, tenant_id)

        # -------------------------------------------------
        # Load ticket
        # -------------------------------------------------

        ticket = db.execute(
            text(
                """
                SELECT id, subject, body
                FROM tickets
                WHERE id = :ticket_id
                """
            ),
            {"ticket_id": job["ticket_id"]},
        ).mappings().first()

        if ticket is None:
            print("Ticket not found")
            return

        # -------------------------------------------------
        # Embed ticket
        # -------------------------------------------------

        query = f"{ticket['subject']}\n{ticket['body']}"

        embedding = embed_text(query)

        # -------------------------------------------------
        # Vector search
        # -------------------------------------------------

        rows = db.execute(
            text("""
                SELECT
                    id,
                    title,
                    body,
                    embedding <=> CAST(:embedding AS vector) AS distance
                FROM kb_articles
                ORDER BY embedding <=> CAST(:embedding AS vector)
                LIMIT :k
            """),
            {
                "embedding": str(embedding),
                "k": TOP_K,
            },
        ).mappings().all()

        chunk_ids = [str(r["id"]) for r in rows]

        print("\nTop Retrieved Articles")

        for r in rows:
            dist = r["distance"]
            print(
                f"{r['id']} | "
                f"{r['title']} | "
                f"distance={(dist or 0):.4f}"
            )

        # -------------------------------------------------
        # Enqueue Draft job
        # -------------------------------------------------

        redis_client.lpush(
            "draft",
            json.dumps(
                {
                    "ticket_id": job["ticket_id"],
                    "tenant_id": tenant_id,
                    "chunk_ids": chunk_ids,
                }
            ),
        )

        db.commit()

        print("Draft job queued.")

    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


def worker():
    print("Retriever worker started...")

    while True:
        item = redis_client.brpop("retrieve", timeout=5)

        if item is None:
            continue

        _, payload = item

        try:
            job = json.loads(payload)
        except json.JSONDecodeError:
            print(f"[BAD JOB] Skipping invalid payload: {payload}")
            continue

        # extra safety (VERY useful in distributed systems)
        if not isinstance(job, dict):
            print(f"[BAD FORMAT] Expected dict, got: {type(job)} → {payload}")
            continue

        process_job(job)


if __name__ == "__main__":
    worker()