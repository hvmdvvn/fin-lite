import json

from jinja2 import Template
from sqlalchemy import text

from app.db.session import SessionLocal
from app.core.tenancy import set_tenant_context
from app.core.queue import get_next_qa_job
from app.agents.llm import generate_reply

THRESHOLD = 0.80

PROMPT_PATH = "app/agents/prompts/qa_v1.txt"


def load_prompt():
    with open(PROMPT_PATH, "r", encoding="utf-8") as f:
        return f.read()


def process_job(job):

    db = SessionLocal()

    try:

        ticket_id = job["ticket_id"]
        tenant_id = job["tenant_id"]

        set_tenant_context(db, tenant_id)

        # -----------------------------
        # Load latest reply
        # -----------------------------

        reply = db.execute(
            text("""
                SELECT id, draft
                FROM replies
                WHERE ticket_id = :ticket_id
                ORDER BY created_at DESC
                LIMIT 1
            """),
            {"ticket_id": ticket_id},
        ).mappings().first()

        if reply is None:
            print("Reply not found")
            return

        # -----------------------------
        # Load KB articles
        # -----------------------------

        kb_rows = db.execute(
            text("""
                SELECT title, body
                FROM kb_articles
            """)
        ).mappings().all()

        kb_text = "\n\n".join(
            f"{row['title']}\n{row['body']}"
            for row in kb_rows
        )

        template = Template(load_prompt())

        prompt = template.render(
            draft=reply["draft"],
            kb=kb_text,
        )

        response = generate_reply(prompt)

        print("Raw QA response:")
        print(repr(response))

        # Remove markdown code fences if LLM returns ```json ... ```
        clean_response = response.strip()

        if clean_response.startswith("```"):
            clean_response = (
                clean_response
                .replace("```json", "")
                .replace("```", "")
                .strip()
            )

        result = json.loads(clean_response)

        unsupported = result.get("unsupported_claims", [])

        confidence = (
            0.0
            if unsupported
            else result.get("confidence", 0.0)
        )

        # -----------------------------
        # Update ticket confidence
        # -----------------------------

        db.execute(
            text("""
                UPDATE tickets
                SET confidence=:confidence
                WHERE id=:ticket_id
            """),
            {
                "confidence": confidence,
                "ticket_id": ticket_id,
            },
        )

        if confidence >= THRESHOLD:

            db.execute(
                text("""
                    UPDATE replies
                    SET sent=true
                    WHERE id=:reply_id
                """),
                {"reply_id": reply["id"]},
            )

            db.execute(
                text("""
                    UPDATE tickets
                    SET status='sent'
                    WHERE id=:ticket_id
                """),
                {"ticket_id": ticket_id},
            )

            print(f"✓ Ticket {ticket_id} auto-sent")

        else:

            db.execute(
                text("""
                    UPDATE tickets
                    SET status='needs_review'
                    WHERE id=:ticket_id
                """),
                {"ticket_id": ticket_id},
            )

            print(f"✓ Ticket {ticket_id} routed to human review")

        db.commit()

    finally:
        db.close()


def worker():

    print("QA Worker Started")

    while True:

        job = get_next_qa_job()

        if job is None:
            continue

        process_job(job)


if __name__ == "__main__":
    worker()