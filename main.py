from fastapi import FastAPI

from app.api.tickets import router as tickets_router
from app.api.debug import router as debug_router
from app.api.kb import router as kb_router


app = FastAPI()

app.include_router(tickets_router)
app.include_router(debug_router)
app.include_router(kb_router)


@app.get("/")
def health():
    return {"status": "ok"}