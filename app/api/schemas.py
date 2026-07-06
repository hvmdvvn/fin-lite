from pydantic import BaseModel


class TicketCreate(BaseModel):
    subject: str
    body: str


class TicketResponse(BaseModel):
    ticket_id: str
    status: str