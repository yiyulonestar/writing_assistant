"""世界观设定接口：CRUD + embedding 同步。"""
import uuid

from fastapi import APIRouter, HTTPException, Query, status

from app.models.world import WorldSetting
from app.schemas.world import WorldSettingCreate, WorldSettingRead, WorldSettingUpdate
from app.services.settings import sync_world_setting_embedding

router = APIRouter()


@router.get("", response_model=list[WorldSettingRead])
async def list_world_settings(
    novel_id: uuid.UUID, category: str | None = Query(default=None)
) -> list[WorldSettingRead]:
    qs = WorldSetting.filter(novel_id=novel_id)
    if category:
        qs = qs.filter(category=category)
    rows = await qs.order_by("category", "name").values()
    return [WorldSettingRead(**r) for r in rows]


@router.post("", response_model=WorldSettingRead, status_code=status.HTTP_201_CREATED)
async def create_world_setting(payload: WorldSettingCreate) -> WorldSettingRead:
    setting = await WorldSetting.create(**payload.model_dump())
    await sync_world_setting_embedding(setting)
    return WorldSettingRead.model_validate(setting)


@router.get("/{setting_id}", response_model=WorldSettingRead)
async def get_world_setting(setting_id: uuid.UUID) -> WorldSettingRead:
    setting = await WorldSetting.get_or_none(id=setting_id)
    if setting is None:
        raise HTTPException(status_code=404, detail="World setting not found")
    return WorldSettingRead.model_validate(setting)


@router.patch("/{setting_id}", response_model=WorldSettingRead)
async def update_world_setting(
    setting_id: uuid.UUID, payload: WorldSettingUpdate
) -> WorldSettingRead:
    setting = await WorldSetting.get_or_none(id=setting_id)
    if setting is None:
        raise HTTPException(status_code=404, detail="World setting not found")
    setting.update_from_dict(payload.model_dump(exclude_unset=True))
    await setting.save()
    await sync_world_setting_embedding(setting)
    return WorldSettingRead.model_validate(setting)


@router.delete("/{setting_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_world_setting(setting_id: uuid.UUID) -> None:
    deleted = await WorldSetting.filter(id=setting_id).delete()
    if not deleted:
        raise HTTPException(status_code=404, detail="World setting not found")
