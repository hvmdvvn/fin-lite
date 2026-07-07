import pytest
import uuid

from sqlalchemy import text

from app.db.session import SessionLocal
from app.core.tenancy import set_tenant_context


# -------------------------------------------------
# Database session fixture
# -------------------------------------------------

@pytest.fixture
def db_session():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.rollback()
        db.close()



# -------------------------------------------------
# Tenant Fixtures
# -------------------------------------------------

@pytest.fixture
def tenant_a(db_session):

    tenant_id = str(
        uuid.UUID(
            "550e8400-e29b-41d4-a716-446655440000"
        )
    )


    db_session.execute(
        text("""
            INSERT INTO tenants
            (
                id,
                name,
                plan
            )
            VALUES
            (
                :id,
                'Tenant A',
                'free'
            )
            ON CONFLICT DO NOTHING
        """),
        {
            "id": tenant_id
        }
    )


    db_session.commit()


    return tenant_id



@pytest.fixture
def tenant_b(db_session):

    tenant_id = str(
        uuid.UUID(
            "660e8400-e29b-41d4-a716-446655440000"
        )
    )


    db_session.execute(
        text("""
            INSERT INTO tenants
            (
                id,
                name,
                plan
            )
            VALUES
            (
                :id,
                'Tenant B',
                'free'
            )
            ON CONFLICT DO NOTHING
        """),
        {
            "id": tenant_id
        }
    )


    db_session.commit()


    return tenant_id



# -------------------------------------------------
# Tenant Context Helper
# -------------------------------------------------

def set_test_tenant(db_session, tenant_id):
    """Set the tenant context for the database session."""
    db_session.execute(
        text(
            """
            SET app.tenant_id = :tenant_id
            """
        ),
        {
            "tenant_id": str(tenant_id)
        }
    )



# -------------------------------------------------
# Ticket Factory
# -------------------------------------------------

@pytest.fixture
def create_ticket(db_session):

    def _create(
        tenant_id,
        subject="Test Ticket",
        body="Sample ticket body",
        status="new"
    ):


        set_test_tenant(
            db_session,
            tenant_id
        )


        result = db_session.execute(
            text("""
                INSERT INTO tickets
                (
                    tenant_id,
                    subject,
                    body,
                    status
                )
                VALUES
                (
                    :tenant_id,
                    :subject,
                    :body,
                    :status
                )
                RETURNING id
            """),
            {
                "tenant_id": tenant_id,
                "subject": subject,
                "body": body,
                "status": status
            }
        )


        ticket_id = result.fetchone()[0]


        db_session.commit()


        return ticket_id


    return _create



# -------------------------------------------------
# KB Article Factory
# -------------------------------------------------

@pytest.fixture
def create_kb_article(db_session):

    def _create(
        tenant_id,
        title="Sample KB Article",
        body="Sample knowledge article"
    ):


        set_test_tenant(
            db_session,
            tenant_id
        )


        result = db_session.execute(
            text("""
                INSERT INTO kb_articles
                (
                    tenant_id,
                    title,
                    body
                )
                VALUES
                (
                    :tenant_id,
                    :title,
                    :body
                )
                RETURNING id
            """),
            {
                "tenant_id": tenant_id,
                "title": title,
                "body": body
            }
        )


        article_id = result.fetchone()[0]


        db_session.commit()


        return article_id


    return _create



# -------------------------------------------------
# Reply Factory
# -------------------------------------------------

@pytest.fixture
def create_reply(db_session):

    def _create(
        tenant_id,
        ticket_id,
        draft="AI generated response",
        sent=False
    ):


        set_test_tenant(
            db_session,
            tenant_id
        )


        result = db_session.execute(
            text("""
                INSERT INTO replies
                (
                    tenant_id,
                    ticket_id,
                    draft,
                    sent,
                    prompt_version
                )
                VALUES
                (
                    :tenant_id,
                    :ticket_id,
                    :draft,
                    :sent,
                    'test-v1'
                )
                RETURNING id
            """),
            {
                "tenant_id": tenant_id,
                "ticket_id": ticket_id,
                "draft": draft,
                "sent": sent
            }
        )


        reply_id = result.fetchone()[0]


        db_session.commit()


        return reply_id


    return _create



# -------------------------------------------------
# Feedback Factory
# -------------------------------------------------

@pytest.fixture
def create_feedback(db_session):

    def _create(
        tenant_id,
        ticket_id,
        action="corrected",
        reviewer="test-user"
    ):


        set_test_tenant(
            db_session,
            tenant_id
        )


        result = db_session.execute(
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
                    :tenant_id,
                    :ticket_id,
                    :reviewer,
                    :action
                )
                RETURNING id
            """),
            {
                "tenant_id": tenant_id,
                "ticket_id": ticket_id,
                "reviewer": reviewer,
                "action": action
            }
        )


        feedback_id = result.fetchone()[0]


        db_session.commit()


        return feedback_id


    return _create
