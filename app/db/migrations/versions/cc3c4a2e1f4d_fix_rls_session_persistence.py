"""fix rls session persistence

Revision ID: cc3c4a2e1f4d
Revises: 0003_fix_rls
Create Date: 2026-07-07 14:10:00.000000

"""
from alembic import op


revision = "0004_fix_rls_persistence"
down_revision = "0003_fix_rls"


def upgrade():
    # Drop existing policies
    policies = [
        ("tickets", "tenant_isolation_tickets"),
        ("kb_articles", "tenant_isolation_kb"),
        ("replies", "tenant_isolation_replies"),
        ("feedback_events", "tenant_isolation_feedback"),
    ]

    for table, policy in policies:
        op.execute(f"DROP POLICY IF EXISTS {policy} ON {table};")

    # Recreate policies with proper tenant context handling
    # The policy now checks if tenant_id matches the current setting
    # When app.tenant_id is not set (empty or null), queries return no results
    op.execute(
        """
        CREATE POLICY tenant_isolation_tickets ON tickets
        FOR SELECT
        USING (
            tenant_id = current_setting('app.tenant_id', true)::uuid
        )
        WITH CHECK (
            tenant_id = current_setting('app.tenant_id', true)::uuid
        );
        """
    )

    op.execute(
        """
        CREATE POLICY tenant_isolation_kb ON kb_articles
        FOR SELECT
        USING (
            tenant_id = current_setting('app.tenant_id', true)::uuid
        )
        WITH CHECK (
            tenant_id = current_setting('app.tenant_id', true)::uuid
        );
        """
    )

    op.execute(
        """
        CREATE POLICY tenant_isolation_replies ON replies
        FOR SELECT
        USING (
            tenant_id = current_setting('app.tenant_id', true)::uuid
        )
        WITH CHECK (
            tenant_id = current_setting('app.tenant_id', true)::uuid
        );
        """
    )

    op.execute(
        """
        CREATE POLICY tenant_isolation_feedback ON feedback_events
        FOR SELECT
        USING (
            tenant_id = current_setting('app.tenant_id', true)::uuid
        )
        WITH CHECK (
            tenant_id = current_setting('app.tenant_id', true)::uuid
        );
        """
    )


def downgrade():
    pass
