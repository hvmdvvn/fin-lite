from fastapi import APIRouter, Depends
from sqlalchemy import text

from app.core.dependencies import get_tenant_db
from app.rag.chunking import chunk_text
from app.rag.embed import embed_text

router = APIRouter()

@router.post("/kb/articles")
def create_kb_article(payload: dict, db=Depends(get_tenant_db)):

    title = payload["title"]
    body = payload["body"]

    chunks = chunk_text(body)

    for chunk in chunks:
        embedding = embed_text(chunk)

        db.execute(
            text("""
                INSERT INTO kb_articles (tenant_id, title, body, embedding)
                VALUES (
                    current_setting('app.tenant_id')::uuid,
                    :title,
                    :body,
                    :embedding
                )
            """),
            {
                "title": title,
                "body": chunk,
                "embedding": embedding
            }
        )

    db.commit()

    return {
        "status": "stored",
        "chunks": len(chunks)
    }