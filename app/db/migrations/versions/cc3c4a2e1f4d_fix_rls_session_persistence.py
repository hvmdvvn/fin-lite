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
    # Separate SELECT policy from INSERT/UPDATE/DELETE policies
    
    # Tickets policies
    op.execute(
        """
        CREATE POLICY tenant_isolation_tickets_select ON tickets
        FOR SELECT
        USING (
            tenant_id = current_setting('app.tenant_id', true)::uuid
        );
        """
    )
    
    op.execute(
        """
        CREATE POLICY tenant_isolation_tickets_write ON tickets
        FOR INSERT
        WITH CHECK (
            tenant_id = current_setting('app.tenant_id', true)::uuid
        );
        """
    )
    
    op.execute(
        """
        CREATE POLICY tenant_isolation_tickets_update ON tickets
        FOR UPDATE
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
        CREATE POLICY tenant_isolation_tickets_delete ON tickets
        FOR DELETE
        USING (
            tenant_id = current_setting('app.tenant_id', true)::uuid
        );
        """
    )

    # KB Articles policies
    op.execute(
        """
        CREATE POLICY tenant_isolation_kb_select ON kb_articles
        FOR SELECT
        USING (
            tenant_id = current_setting('app.tenant_id', true)::uuid
        );
        """
    )
    
    op.execute(
        """
        CREATE POLICY tenant_isolation_kb_write ON kb_articles
        FOR INSERT
        WITH CHECK (
            tenant_id = current_setting('app.tenant_id', true)::uuid
        );
        """
    )
    
    op.execute(
        """
        CREATE POLICY tenant_isolation_kb_update ON kb_articles
        FOR UPDATE
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
        CREATE POLICY tenant_isolation_kb_delete ON kb_articles
        FOR DELETE
        USING (
            tenant_id = current_setting('app.tenant_id', true)::uuid
        );
        """
    )

    # Replies policies
    op.execute(
        """
        CREATE POLICY tenant_isolation_replies_select ON replies
        FOR SELECT
        USING (
            tenant_id = current_setting('app.tenant_id', true)::uuid
        );
        """
    )
    
    op.execute(
        """
        CREATE POLICY tenant_isolation_replies_write ON replies
        FOR INSERT
        WITH CHECK (
            tenant_id = current_setting('app.tenant_id', true)::uuid
        );
        """
    )
    
    op.execute(
        """
        CREATE POLICY tenant_isolation_replies_update ON replies
        FOR UPDATE
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
        CREATE POLICY tenant_isolation_replies_delete ON replies
        FOR DELETE
        USING (
            tenant_id = current_setting('app.tenant_id', true)::uuid
        );
        """
    )

    # Feedback Events policies
    op.execute(
        """
        CREATE POLICY tenant_isolation_feedback_select ON feedback_events
        FOR SELECT
        USING (
            tenant_id = current_setting('app.tenant_id', true)::uuid
        );
        """
    )
    
    op.execute(
        """
        CREATE POLICY tenant_isolation_feedback_write ON feedback_events
        FOR INSERT
        WITH CHECK (
            tenant_id = current_setting('app.tenant_id', true)::uuid
        );
        """
    )
    
    op.execute(
        """
        CREATE POLICY tenant_isolation_feedback_update ON feedback_events
        FOR UPDATE
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
        CREATE POLICY tenant_isolation_feedback_delete ON feedback_events
        FOR DELETE
        USING (
            tenant_id = current_setting('app.tenant_id', true)::uuid
        );
        """
    )


def downgrade():
    pass
