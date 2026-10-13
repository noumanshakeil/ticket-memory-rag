from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from backend.db import get_db
from backend.services import memory as svc

router = APIRouter()
templates = Jinja2Templates(directory="backend/templates")

@router.get("/", response_class=HTMLResponse)
async def home(request: Request, db: AsyncSession = Depends(get_db)):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "title": "Ticket Memory RAG",
            "tickets": await svc.list_tickets(db),
            "draft": None,
            "similar": [],
        },
    )

@router.post("/ui/tickets")
async def ui_add(
    subject: str = Form(...),
    body: str = Form(...),
    resolution: str = Form(""),
    tags: str = Form(""),
    db: AsyncSession = Depends(get_db),
):
    await svc.add_ticket(db, subject, body, resolution, tags)
    return RedirectResponse("/", status_code=303)

@router.post("/ui/assist", response_class=HTMLResponse)
async def ui_assist(
    request: Request,
    subject: str = Form(...),
    body: str = Form(...),
    db: AsyncSession = Depends(get_db),
):
    result = await svc.assist(db, subject, body)
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "title": "Ticket Memory RAG",
            "tickets": await svc.list_tickets(db),
            "draft": result["draft_reply"],
            "similar": result["similar"],
            "subject": subject,
            "body": body,
        },
    )
