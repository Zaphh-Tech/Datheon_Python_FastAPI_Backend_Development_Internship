from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.db.models import Note, User
from app.routers.auth import get_current_user
from app.schemas.note import NoteCreate, NoteOut, NoteUpdate

router = APIRouter(prefix="/notes", tags=["Notes"])


async def _owned_note(note_id: int, user: User, db: AsyncSession) -> Note:
    note = (
        await db.execute(select(Note).where(Note.id == note_id, Note.owner_id == user.id))
    ).scalar_one_or_none()
    if note is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Note {note_id} not found")
    return note


@router.get("", response_model=list[NoteOut])
async def list_notes(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    rows = (
        await db.execute(select(Note).where(Note.owner_id == user.id).order_by(Note.id))
    ).scalars().all()
    return list(rows)


@router.post("", response_model=NoteOut, status_code=status.HTTP_201_CREATED)
async def create_note(
    payload: NoteCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    note = Note(title=payload.title, content=payload.content, owner_id=user.id)
    db.add(note)
    await db.commit()
    await db.refresh(note)
    return note


@router.get("/{note_id}", response_model=NoteOut)
async def get_note(
    note_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await _owned_note(note_id, user, db)


@router.put("/{note_id}", response_model=NoteOut)
async def update_note(
    note_id: int,
    payload: NoteUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    note = await _owned_note(note_id, user, db)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(note, field, value)
    await db.commit()
    await db.refresh(note)
    return note


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_note(
    note_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    note = await _owned_note(note_id, user, db)
    await db.delete(note)
    await db.commit()
    return None
