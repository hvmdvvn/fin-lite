from fastapi import APIRouter, Depends
from sqlalchemy import text

from app.core.dependencies import get_tenant_db
from app.core.queue import enqueue_classify, enqueue_reembed
from app.api.schemas import TicketCreate, ReviewCreate

router = APIRouter()


@router.post("/tickets", status_code=202)
def create_ticket(
    payload: TicketCreate,
    ctx=Depends(get_tenant_db)
):

    db, tenant_id = ctx

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

    # FIX HERE
    enqueue_classify(str(ticket_id), tenant_id)

    return {
        "ticket_id": str(ticket_id),
        "status": "new"
    }

@router.get("/tickets/{ticket_id}")
def get_ticket(
    ticket_id: str,
    ctx=Depends(get_tenant_db)
):

    db, tenant_id = ctx

    result = db.execute(
        text("SELECT * FROM tickets WHERE id = :id"),
        {"id": ticket_id},
    ).fetchone()

    if not result:
        return {"error": "not found"}

    return dict(result._mapping)


@router.post("/tickets/{ticket_id}/review")
def submit_review(
    ticket_id: str,
    payload: ReviewCreate,
    ctx=Depends(get_tenant_db)
):

    db, tenant_id = ctx

    # -----------------------------
    # Save feedback event
    # -----------------------------

    db.execute(
        text("""
            INSERT INTO feedback_events
            (
                tenant_id,
                ticket_id,
                reviewer,
                action
            )
            VALUES
            (
                current_setting('app.tenant_id')::uuid,
                :ticket_id,
                :reviewer,
                :action
            )
        """),
        {
            "ticket_id": ticket_id,
            "reviewer": payload.reviewer,
            "action": payload.action,
        },
    )


    reembed_scheduled = False


    # -----------------------------
    # Human correction
    # -----------------------------

    if payload.action == "corrected":

        if not payload.reviewer_edit:
            return {
                "error": "reviewer_edit required"
            }


        db.execute(
            text("""
                UPDATE replies
                SET reviewer_edit=:edit
                WHERE ticket_id=:ticket_id
            """),
            {
                "edit": payload.reviewer_edit,
                "ticket_id": ticket_id,
            },
        )


        db.execute(
            text("""
                UPDATE tickets
                SET status='resolved'
                WHERE id=:ticket_id
            """),
            {
                "ticket_id": ticket_id
            },
        )


        # -----------------------------
        # Get tenant safely
        # -----------------------------

        tenant = db.execute(
            text("""
                SELECT tenant_id
                FROM tickets
                WHERE id=:ticket_id
            """),
            {
                "ticket_id": ticket_id
            },
        ).fetchone()

        if not tenant:
            return {
                "error": "ticket not found"
            }


        enqueue_reembed(
            ticket_id=ticket_id,
            tenant_id=str(tenant[0]),
            correction=payload.reviewer_edit
        )


        reembed_scheduled = True


    db.commit()


    return {
        "ticket_id": ticket_id,
        "reembed_scheduled": reembed_scheduled
    }