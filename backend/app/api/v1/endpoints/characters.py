"""角色设定接口：CRUD + embedding 同步。"""
import uuid

from fastapi import APIRouter, HTTPException, status

from app.models.character import Character
from app.schemas.character import CharacterCreate, CharacterRead, CharacterUpdate
from app.services.settings import sync_character_embedding

router = APIRouter()


@router.get("", response_model=list[CharacterRead])
async def list_characters(novel_id: uuid.UUID) -> list[CharacterRead]:
    rows = await Character.filter(novel_id=novel_id).order_by("name").values()
    return [CharacterRead(**r) for r in rows]


@router.post("", response_model=CharacterRead, status_code=status.HTTP_201_CREATED)
async def create_character(payload: CharacterCreate) -> CharacterRead:
    character = await Character.create(**payload.model_dump())
    await sync_character_embedding(character)
    return CharacterRead.model_validate(character)


@router.get("/{character_id}", response_model=CharacterRead)
async def get_character(character_id: uuid.UUID) -> CharacterRead:
    character = await Character.get_or_none(id=character_id)
    if character is None:
        raise HTTPException(status_code=404, detail="Character not found")
    return CharacterRead.model_validate(character)


@router.patch("/{character_id}", response_model=CharacterRead)
async def update_character(character_id: uuid.UUID, payload: CharacterUpdate) -> CharacterRead:
    character = await Character.get_or_none(id=character_id)
    if character is None:
        raise HTTPException(status_code=404, detail="Character not found")
    character.update_from_dict(payload.model_dump(exclude_unset=True))
    await character.save()
    await sync_character_embedding(character)
    return CharacterRead.model_validate(character)


@router.delete("/{character_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_character(character_id: uuid.UUID) -> None:
    deleted = await Character.filter(id=character_id).delete()
    if not deleted:
        raise HTTPException(status_code=404, detail="Character not found")
