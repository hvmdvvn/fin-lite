import jwt

token = jwt.encode(
    {"tenant_id": "550e8400-e29b-41d4-a716-446655440000"},
    "dev-secret",
    algorithm="HS256"
)

print(token)