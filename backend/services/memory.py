from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.llm import get_llm
from backend.models import Ticket
from backend.services.rag_core import score_chunk


async def add_ticket(
    session: AsyncSession,
    subject: str,
    body: str,
    resolution: str = "",
    tags: str = "",
    status: str = "resolved",
) -> Ticket:
    t = Ticket(
        id=uuid.uuid4().hex[:10],
        subject=subject.strip()[:240],
        body=body.strip(),
        resolution=resolution.strip(),
        tags=tags.strip()[:200],
        status=status[:32],
    )
    session.add(t)
    await session.commit()
    await session.refresh(t)
    return t


async def list_tickets(session: AsyncSession, limit: int = 50) -> list[Ticket]:
    return list(
        (await session.execute(select(Ticket).order_by(Ticket.created_at.desc()).limit(limit))).scalars()
    )


async def similar(session: AsyncSession, text: str, *, k: int = 5) -> list[dict]:
    rows = list((await session.execute(select(Ticket))).scalars())
    scored = []
    blob_query = text
    for t in rows:
        corpus = f"{t.subject}\n{t.body}\n{t.resolution}\n{t.tags}"
        s = score_chunk(blob_query, corpus)
        if s <= 0:
            continue
        scored.append(
            {
                "id": t.id,
                "subject": t.subject,
                "score": round(s, 3),
                "tags": t.tags,
                "resolution": t.resolution[:400],
                "status": t.status,
            }
        )
    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:k]


async def assist(session: AsyncSession, subject: str, body: str) -> dict:
    neighbors = await similar(session, f"{subject}\n{body}", k=5)
    memory = "\n\n".join(
        f"- ({n['score']}) {n['subject']}: {n['resolution'] or 'no resolution recorded'}"
        for n in neighbors
    ) or "(no similar tickets)"
    llm = get_llm()
    draft = await llm.complete(
        f"Draft a support reply using similar past tickets.\n"
        f"NEW TICKET:\n{subject}\n{body}\n\nSIMILAR:\n{memory}",
        system="Support engineer. Be empathetic, concrete, and reference prior fixes cautiously.",
    )
    return {"draft_reply": draft, "similar": neighbors}
