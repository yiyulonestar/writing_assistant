"""时间线事件接口：CRUD + embedding 同步 + 一致性校验（防前后矛盾）。"""
import uuid

from fastapi import APIRouter, HTTPException, status

from app.models.timeline import TimelineEvent
from app.schemas.timeline import TimelineEventCreate, TimelineEventRead, TimelineEventUpdate
from app.services.settings import sync_timeline_event_embedding

router = APIRouter()


@router.get("", response_model=list[TimelineEventRead])
async def list_timeline(novel_id: uuid.UUID) -> list[TimelineEventRead]:
    rows = await TimelineEvent.filter(novel_id=novel_id).order_by("order_index").values()
    return [TimelineEventRead(**r) for r in rows]


@router.post("", response_model=TimelineEventRead, status_code=status.HTTP_201_CREATED)
async def create_timeline_event(payload: TimelineEventCreate) -> TimelineEventRead:
    event = await TimelineEvent.create(**payload.model_dump())
    await sync_timeline_event_embedding(event)
    return TimelineEventRead.model_validate(event)


@router.get("/{event_id}", response_model=TimelineEventRead)
async def get_timeline_event(event_id: uuid.UUID) -> TimelineEventRead:
    event = await TimelineEvent.get_or_none(id=event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="Timeline event not found")
    return TimelineEventRead.model_validate(event)


@router.patch("/{event_id}", response_model=TimelineEventRead)
async def update_timeline_event(
    event_id: uuid.UUID, payload: TimelineEventUpdate
) -> TimelineEventRead:
    event = await TimelineEvent.get_or_none(id=event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="Timeline event not found")
    event.update_from_dict(payload.model_dump(exclude_unset=True))
    await event.save()
    await sync_timeline_event_embedding(event)
    return TimelineEventRead.model_validate(event)


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_timeline_event(event_id: uuid.UUID) -> None:
    deleted = await TimelineEvent.filter(id=event_id).delete()
    if not deleted:
        raise HTTPException(status_code=404, detail="Timeline event not found")
