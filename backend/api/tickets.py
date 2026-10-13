from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from backend.db import get_db
from backend.services import memory as svc

class TicketIn(BaseModel):
    subject: str = Field(min_length=3)
    body: str = Field(min_length=5)
    resolution: str = ""
    tags: str = ""
    status: str = "resolved"

class AssistIn(BaseModel):
    subject: str = Field(min_length=3)
    body: str = Field(min_length=5)

router = APIRouter()

@router.get("/tickets")
async def list_tickets(db: AsyncSession = Depends(get_db)):
    rows = await svc.list_tickets(db)
    return {
        "tickets": [
            {"id": t.id, "subject": t.subject, "tags": t.tags, "status": t.status}
            for t in rows
        ]
    }

@router.post("/tickets")
async def create(payload: TicketIn, db: AsyncSession = Depends(get_db)):
    t = await svc.add_ticket(
        db, payload.subject, payload.body, payload.resolution, payload.tags, payload.status
    )
    return {"id": t.id}

@router.post("/similar")
async def similar(payload: AssistIn, db: AsyncSession = Depends(get_db)):
    return {"similar": await svc.similar(db, f"{payload.subject}\n{payload.body}")}

@router.post("/assist")
async def assist(payload: AssistIn, db: AsyncSession = Depends(get_db)):
    return await svc.assist(db, payload.subject, payload.body)
