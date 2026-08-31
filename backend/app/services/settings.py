"""设定管理服务：角色 / 世界观 / 时间线的 embedding 同步与检索。

生成时从这里按「本章涉及的角色 / 地点 / 事件」召回相关设定，并拼装成
「事实清单」注入提示词，用于一致性约束。
"""
from __future__ import annotations

import logging
import uuid

from tortoise import connections
from tortoise.expressions import Q

from app.embeddings.client import get_embedding_client
from app.models.character import Character
from app.models.timeline import TimelineEvent
from app.models.world import WorldSetting

logger = logging.getLogger(__name__)


# ---------- 文本拼装（供 embedding 与事实清单复用） ----------

def _character_text(c: Character) -> str:
    parts = [f"角色：{c.name}"]
    if c.aliases:
        parts.append(f"别名：{'、'.join(c.aliases)}")
    if c.role:
        parts.append(f"定位：{c.role}")
    for label, val in (
        ("性格", c.personality),
        ("背景", c.background),
        ("外貌", c.appearance),
        ("目标", c.goals),
    ):
        if val:
            parts.append(f"{label}：{val}")
    return "\n".join(parts)


def _world_text(w: WorldSetting) -> str:
    parts = [f"[{w.category}] {w.name}"]
    if w.description:
        parts.append(w.description)
    if w.notes:
        parts.append(w.notes)
    return "\n".join(parts)


def _timeline_text(t: TimelineEvent) -> str:
    parts = [f"事件：{t.title}"]
    if t.time_point:
        parts.append(f"时间：{t.time_point}")
    if t.description:
        parts.append(t.description)
    return "\n".join(parts)


# ---------- embedding 同步 ----------

async def _encode_safe(text: str) -> list[float] | None:
    """编码一段文本；失败时记录警告并返回 None（跳过 embedding，不阻断写入）。"""
    try:
        return (await get_embedding_client().aencode([text]))[0]
    except Exception as exc:  # noqa: BLE001 — 嵌入是可选能力，失败不阻断 CRUD
        logger.warning("embedding 编码失败（跳过）：%s", exc)
        return None


async def sync_character_embedding(character: Character) -> None:
    vec = await _encode_safe(_character_text(character))
    if vec is not None:
        character.embedding = vec
        await character.save(update_fields=["embedding"])


async def sync_world_setting_embedding(setting: WorldSetting) -> None:
    vec = await _encode_safe(_world_text(setting))
    if vec is not None:
        setting.embedding = vec
        await setting.save(update_fields=["embedding"])


async def sync_timeline_event_embedding(event: TimelineEvent) -> None:
    vec = await _encode_safe(_timeline_text(event))
    if vec is not None:
        event.embedding = vec
        await event.save(update_fields=["embedding"])


# ---------- 向量召回 ----------

def _vec_str(vec: list[float]) -> str:
    return "[" + ",".join(str(round(float(x), 6)) for x in vec) + "]"


async def recall_by_embedding(model, novel_id: uuid.UUID, query_text: str, top_k: int = 5):
    """对指定模型按 pgvector 余弦相似度召回 top-k（返回模型实例列表）。

    依赖 pgvector / 本地 embedding；失败时记录警告并返回空列表，回退到结构化查询。
    """
    try:
        qvec = await get_embedding_client().aencode_query(query_text)
        table = model._meta.db_table
        conn = connections.get("default")
        sql = (
            f"SELECT id FROM {table} "
            "WHERE novel_id = $1 AND embedding IS NOT NULL "
            "ORDER BY embedding <=> $2::vector LIMIT $3"
        )
        rows = await conn.execute_query_dict(sql, [str(novel_id), _vec_str(qvec), top_k])
        ids = [row["id"] for row in rows]
    except Exception as exc:  # noqa: BLE001 — 向量召回是增强能力，失败回退结构化查询
        logger.warning("向量召回失败（回退结构化查询）：%s", exc)
        return []
    if not ids:
        return []
    return await model.filter(id__in=ids).all()


# ---------- 事实清单 ----------

async def build_fact_sheet(
    novel_id: uuid.UUID,
    character_names: list[str] | None = None,
    world_keywords: list[str] | None = None,
    timeline_keywords: list[str] | None = None,
    query_text: str | None = None,
) -> str:
    """组装事实清单：结构化精确查询 + 向量召回，渲染为紧凑文本块。"""
    sections: list[str] = []

    characters: list[Character] = []
    if character_names:
        characters = await Character.filter(novel_id=novel_id, name__in=character_names).all()
    if query_text:
        recalled = await recall_by_embedding(Character, novel_id, query_text, top_k=5)
        seen = {c.id for c in characters}
        characters += [c for c in recalled if c.id not in seen]
    if characters:
        sections.append("【角色设定】\n" + "\n\n".join(_character_text(c) for c in characters))

    worlds: list[WorldSetting] = []
    if world_keywords:
        q = Q()
        for kw in world_keywords:
            q |= Q(name__icontains=kw)
        worlds = await WorldSetting.filter(novel_id=novel_id).filter(q).all()
    if query_text:
        recalled = await recall_by_embedding(WorldSetting, novel_id, query_text, top_k=5)
        seen = {w.id for w in worlds}
        worlds += [w for w in recalled if w.id not in seen]
    if worlds:
        sections.append("【世界观设定】\n" + "\n\n".join(_world_text(w) for w in worlds))

    timeline: list[TimelineEvent] = []
    if timeline_keywords:
        q = Q()
        for kw in timeline_keywords:
            q |= Q(title__icontains=kw) | Q(description__icontains=kw)
        timeline = await TimelineEvent.filter(novel_id=novel_id).filter(q).all()
    if query_text:
        recalled = await recall_by_embedding(TimelineEvent, novel_id, query_text, top_k=5)
        seen = {t.id for t in timeline}
        timeline += [t for t in recalled if t.id not in seen]
    if timeline:
        sections.append("【时间线事件】\n" + "\n\n".join(_timeline_text(t) for t in timeline))

    return "\n\n".join(sections)
