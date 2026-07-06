from fastapi import APIRouter, Depends
from sqlalchemy import text

from app.core.dependencies import get_tenant_db
from app.core.queue import enqueue_classify
from app.api.schemas import TicketCreate

router = APIRouter()


@router.post("/tickets", status_code=202)
def create_ticket(payload: TicketCreate, db=Depends(get_tenant_db)):

    result = db.execute(
        text("""
            INSERT INTO tickets (tenant_id, subject, body, status)
            VALUES (
                current_setting('app.tenant_id')::uuid,
                :subject,
                :body,
                'new'
            )
            RETURNING id
        """),
        {"subject": payload.subject, "body": payload.body},
    )

    ticket_id = result.fetchone()[0]
    db.commit()

    # enqueue async job
    enqueue_classify(str(ticket_id))

    return {
        "ticket_id": str(ticket_id),
        "status": "new"
    }


@router.get("/tickets/{ticket_id}")
def get_ticket(ticket_id: str, db=Depends(get_tenant_db)):

    result = db.execute(
        text("SELECT * FROM tickets WHERE id = :id"),
        {"id": ticket_id},
    ).fetchone()

    if not result:
        return {"error": "not found"}

    return dict(result._mapping)