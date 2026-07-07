from sqlalchemy import text

from app.core.tenancy import set_tenant_context
from tests.conftest import set_test_tenant



def test_tenant_cannot_read_other_tenant_ticket(
    db_session,
    tenant_a,
    tenant_b
):



    # create ticket as tenant A
    set_test_tenant(
        db_session,
        tenant_a
    )


    ticket = db_session.execute(
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
                :tenant,
                'Tenant A ticket',
                'secret',
                'new'
            )
            RETURNING id
        """),
        {
            "tenant": tenant_a
        }
    ).fetchone()


    ticket_id = ticket[0]


    db_session.commit()


    # switch to tenant B
    set_test_tenant(
        db_session,
        tenant_b
    )


    result = db_session.execute(
        text("""
            SELECT *
            FROM tickets
            WHERE id=:id
        """),
        {
            "id": ticket_id
        }
    ).fetchall()


    assert result == []

def test_tenant_cannot_read_other_tenant_kb(
    db_session,
    tenant_a,
    tenant_b
):



    set_test_tenant(
        db_session,
        tenant_a
    )


    article = db_session.execute(
        text("""
            INSERT INTO kb_articles
            (
                tenant_id,
                title,
                body
            )
            VALUES
            (
                :tenant,
                'Tenant A KB',
                'secret information'
            )
            RETURNING id
        """),
        {
            "tenant": tenant_a
        }
    ).fetchone()


    article_id = article[0]


    db_session.commit()


    set_test_tenant(
        db_session,
        tenant_b
    )


    result = db_session.execute(
        text("""
            SELECT *
            FROM kb_articles
            WHERE id=:id
        """),
        {
            "id":article_id
        }
    ).fetchall()


    assert result == []


def test_without_tenant_context_returns_empty(
    db_session,
    tenant_a
):


    # create ticket under tenant A
    set_test_tenant(
        db_session,
        tenant_a
    )


    db_session.execute(
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
                :tenant,
                'Hidden ticket',
                'data',
                'new'
            )
        """),
        {
            "tenant":tenant_a
        }
    )


    db_session.commit()


    # remove tenant context
    db_session.execute(
        text(
            "RESET app.tenant_id"
        )
    )


    result = db_session.execute(
        text(
            "SELECT * FROM tickets"
        )
    ).fetchall()


    assert result == []