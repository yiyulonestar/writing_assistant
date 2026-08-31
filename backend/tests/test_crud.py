"""CRUD 端点集成测试（SQLite + embedding 打桩）。"""
import pytest


@pytest.mark.asyncio
async def test_novel_crud(client):
    r = await client.post("/api/v1/novels", json={"title": "测试书", "genre": "仙侠"})
    assert r.status_code == 201
    novel = r.json()
    assert novel["title"] == "测试书"

    r = await client.get("/api/v1/novels")
    assert r.status_code == 200 and len(r.json()) == 1

    r = await client.get(f"/api/v1/novels/{novel['id']}")
    assert r.status_code == 200 and r.json()["title"] == "测试书"

    r = await client.patch(f"/api/v1/novels/{novel['id']}", json={"synopsis": "简介"})
    assert r.status_code == 200 and r.json()["synopsis"] == "简介"

    r = await client.delete(f"/api/v1/novels/{novel['id']}")
    assert r.status_code == 204


@pytest.mark.asyncio
async def test_character_crud(client):
    r = await client.post("/api/v1/novels", json={"title": "书"})
    novel_id = r.json()["id"]

    r = await client.post("/api/v1/characters", json={"name": "林辰", "novel_id": novel_id})
    assert r.status_code == 201
    char = r.json()
    assert char["novel_id"] == novel_id

    r = await client.get("/api/v1/characters", params={"novel_id": novel_id})
    assert r.status_code == 200 and len(r.json()) == 1

    r = await client.patch(f"/api/v1/characters/{char['id']}", json={"role": "主角"})
    assert r.status_code == 200 and r.json()["role"] == "主角"

    r = await client.delete(f"/api/v1/characters/{char['id']}")
    assert r.status_code == 204


@pytest.mark.asyncio
async def test_chapter_and_drafts(client):
    r = await client.post("/api/v1/novels", json={"title": "书"})
    novel_id = r.json()["id"]

    r = await client.post(
        "/api/v1/chapters",
        json={"number": 1, "novel_id": novel_id, "content": "第一章正文，共九个字"},
    )
    assert r.status_code == 201
    ch = r.json()
    assert ch["word_count"] == 9  # 自动按中文字符计字

    r = await client.post(f"/api/v1/chapters/{ch['id']}/drafts", json={"content": "草稿v1"})
    assert r.status_code == 201 and r.json()["version"] == 1
    r = await client.post(f"/api/v1/chapters/{ch['id']}/drafts", json={"content": "草稿v2"})
    assert r.json()["version"] == 2

    r = await client.get(f"/api/v1/chapters/{ch['id']}/drafts")
    assert r.status_code == 200 and len(r.json()) == 2

    # 单版本 + diff
    r = await client.get(f"/api/v1/chapters/{ch['id']}/drafts/1")
    assert r.status_code == 200 and r.json()["content"] == "草稿v1"
    r = await client.get(
        f"/api/v1/chapters/{ch['id']}/drafts/2/diff", params={"base": 1}
    )
    assert r.status_code == 200 and len(r.json()["diff"]) > 0


@pytest.mark.asyncio
async def test_timeline_and_world_settings(client):
    r = await client.post("/api/v1/novels", json={"title": "书"})
    novel_id = r.json()["id"]

    r = await client.post(
        "/api/v1/timeline",
        json={"title": "觉醒体质", "novel_id": novel_id, "order_index": 1},
    )
    assert r.status_code == 201
    r = await client.get("/api/v1/timeline", params={"novel_id": novel_id})
    assert r.status_code == 200 and len(r.json()) == 1

    r = await client.post(
        "/api/v1/world-settings",
        json={"category": "宗门", "name": "青云宗", "novel_id": novel_id},
    )
    assert r.status_code == 201
    parent = r.json()
    r = await client.post(
        "/api/v1/world-settings",
        json={"category": "宗门", "name": "外门", "novel_id": novel_id, "parent_id": parent["id"]},
    )
    assert r.status_code == 201 and r.json()["parent_id"] == parent["id"]

    r = await client.get("/api/v1/world-settings", params={"novel_id": novel_id, "category": "宗门"})
    assert r.status_code == 200 and len(r.json()) == 2
