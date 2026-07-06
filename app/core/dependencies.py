from fastapi import Depends
from app.api.auth import verify_jwt
from app.db.session import get_db
from app.core.tenancy import set_tenant_context
from sqlalchemy import text


def get_tenant_db(payload=Depends(verify_jwt), db=Depends(get_db)):
    db.execute(
        text("SET LOCAL app.tenant_id = :tid"),
        {"tid": str(payload["tenant_id"])},
    )
    yield db