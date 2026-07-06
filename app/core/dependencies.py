from fastapi import Depends
from app.api.auth import verify_jwt
from app.db.session import get_db
from sqlalchemy import text


def get_tenant_db(payload=Depends(verify_jwt), db=Depends(get_db)):
    tenant_id = payload["tenant_id"]

    db.execute(
        text("SET LOCAL app.tenant_id = :tid"),
        {"tid": str(tenant_id)},
    )

    try:
        yield db, tenant_id
    finally:
        db.close()