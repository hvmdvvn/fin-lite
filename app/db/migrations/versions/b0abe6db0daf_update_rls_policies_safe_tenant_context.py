"""update rls policies safe tenant context

Revision ID: b0abe6db0daf
Revises: 0001_initial
Create Date: 2026-07-07 14:30:11.471587

"""
from alembic import op


revision = "0002_update_rls"
down_revision = "0001_initial"


def upgrade():

    # tickets
    op.execute("""
        DROP POLICY IF EXISTS tenant_isolation_tickets
        ON tickets;
    """)

    op.execute(
    """
    CREATE POLICY tenant_isolation_tickets
    ON tickets
    USING (
        tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid
    )
    WITH CHECK (
        tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid
    );
    """
    )


    # kb_articles
    op.execute("""
        DROP POLICY IF EXISTS tenant_isolation_kb
        ON kb_articles;
    """)

    op.execute("""
        CREATE POLICY tenant_isolation_kb
        ON kb_articles
        USING (
            tenant_id = current_setting('app.tenant_id', true)::uuid
        )
        WITH CHECK (
            tenant_id = current_setting('app.tenant_id', true)::uuid
        );
    """)


def downgrade():
    pass
