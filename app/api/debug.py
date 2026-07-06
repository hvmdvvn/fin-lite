from fastapi import APIRouter, Depends
from sqlalchemy import text
from app.core.dependencies import get_tenant_db

router = APIRouter()


@router.get("/debug-rls")
def debug_rls(db=Depends(get_tenant_db)):
    identity = db.execute(
        text("""
            SELECT
                current_user,
                session_user,
                current_setting('app.tenant_id', true)
        """)
    ).fetchone()

    bypass = db.execute(
        text("""
            SELECT rolname, rolsuper, rolbypassrls
            FROM pg_roles
            WHERE rolname = current_user
        """)
    ).fetchone()

    pid = db.execute(text("SELECT pg_backend_pid()")).fetchone()

    rows = db.execute(text("SELECT tenant_id FROM tickets")).fetchall()

    return {
        "current_user": identity[0],
        "session_user": identity[1],
        "tenant_setting": identity[2],
        "is_superuser": bypass[1] if bypass else None,
        "bypass_rls": bypass[2] if bypass else None,
        "pid": pid[0],
        "rows_seen": [r[0] for r in rows],
    }