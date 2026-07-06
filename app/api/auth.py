import jwt
from fastapi import Depends, HTTPException, Header

from app.core.config import settings

SECRET = settings.JWT_SECRET


def verify_jwt(authorization: str = Header(...)) -> dict:
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="missing bearer token")

    token = authorization.removeprefix("Bearer ").strip()

    try:
        payload = jwt.decode(token, SECRET, algorithms=["HS256"])
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="invalid token")

    # MUST contain tenant_id
    if "tenant_id" not in payload:
        raise HTTPException(status_code=401, detail="tenant_id missing in token")

    return payload