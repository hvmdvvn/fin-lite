from sqlalchemy import text

from app.db.session import SessionLocal
from app.core.queue import get_next_reembed_job
from app.core.tenancy import set_tenant_context
from app.rag.embed import embed_text



def get_ticket_tenant(db, ticket_id):

    result = db.execute(
        text("""
            SELECT tenant_id
            FROM tickets
            WHERE id=:id
        """),
        {
            "id": ticket_id
        },
    ).fetchone()


    if not result:
        return None


    return str(result[0])



def process_reembed(job):

    db = SessionLocal()

    try:

        ticket_id = job["ticket_id"]

        correction = job["correction"]


        # IMPORTANT:
        # Do NOT trust Redis tenant_id

        tenant_id = job["tenant_id"]


        # Set RLS context FIRST
        set_tenant_context(
            db,
            tenant_id
        )


        # Now verify ticket exists under this tenant

        ticket = db.execute(
            text("""
                SELECT tenant_id
                FROM tickets
                WHERE id=:id
            """),
            {
                "id": ticket_id
            },
        ).fetchone()


        if not ticket:
            print("Ticket not found")
            return


        # Security check
        if str(ticket[0]) != str(tenant_id):
            print("Tenant mismatch detected")
            return


        embedding = embed_text(
            correction
        )


        db.execute(
            text("""
                INSERT INTO kb_articles
                (
                    tenant_id,
                    title,
                    body,
                    embedding
                )
                VALUES
                (
                    :tenant_id,
                    :title,
                    :body,
                    :embedding
                )
            """),
            {
                "tenant_id": tenant_id,
                "title": f"Correction ticket {ticket_id}",
                "body": correction,
                "embedding": embedding,
            },
        )


        db.commit()


        print(
            f"✓ Correction embedded for tenant {tenant_id}"
        )


    except Exception as e:

        db.rollback()

        print(
            "Reembed error:",
            e
        )


    finally:

        db.close()



def worker():

    print("Reembed worker started")


    while True:

        job = get_next_reembed_job()


        if job is None:
            continue


        process_reembed(job)



if __name__ == "__main__":
    worker()