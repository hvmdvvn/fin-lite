"""fix rls empty tenant context

Revision ID: bb2855e4da57
Revises: 0002_update_rls
Create Date: 2026-07-07 14:39:06.654202

"""
from alembic import op


revision = "0003_fix_rls"
down_revision = "0002_update_rls"


def upgrade():

    policies = [
        ("tickets", "tenant_isolation_tickets"),
        ("kb_articles", "tenant_isolation_kb"),
        ("replies", "tenant_isolation_replies"),
        ("feedback_events", "tenant_isolation_feedback"),
    ]

    for table, policy in policies:

        op.execute(
            f"""
            DROP POLICY IF EXISTS {policy}
            ON {table};
            """
        )

        op.execute(
            f"""
            CREATE POLICY {policy}
            ON {table}
            USING (
                tenant_id =
                NULLIF(
                    current_setting('app.tenant_id', true),
                    ''
                )::uuid
            )
            WITH CHECK (
                tenant_id =
                NULLIF(
                    current_setting('app.tenant_id', true),
                    ''
                )::uuid
            );
            """
        )


def downgrade():
    pass
