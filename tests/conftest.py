import pytest

from app.db.session import SessionLocal
from app.core.tenancy import set_tenant_context
from sqlalchemy import text



TENANT_A = "550e8400-e29b-41d4-a716-446655440000"
TENANT_B = "660e8400-e29b-41d4-a716-446655440000"


@pytest.fixture
def db_session():

    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def tenant_a():
    return TENANT_A


@pytest.fixture
def tenant_b():
    return TENANT_B


def set_test_tenant(db, tenant_id):

    db.execute(
        text(
            """
            SET LOCAL app.tenant_id = :tenant_id
            """
        ),
        {
            "tenant_id": str(tenant_id)
        }
    )