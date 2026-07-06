from sqlalchemy import text


def set_tenant_context(db, tenant_id: str):
    db.execute(
        text("SELECT set_config('app.tenant_id', :tid, true)"),
        {"tid": str(tenant_id)},
    )