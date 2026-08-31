"""生成进度 WebSocket 推送。

客户端连接后发送 GenerateChapterRequest JSON，服务端在生成过程中推送进度事件：
  {"stage": "planning"|"retrieving"|"generating"|"reviewing"|"revising"|"persisting"|"summarizing"|"done", ...}
结束后推送 {"stage": "complete", "chapter_id", "word_count"}。
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.schemas.generation import GenerateChapterRequest
from app.services.generation.pipeline import GenerationPipeline

router = APIRouter()


@router.websocket("/ws")
async def generate_progress(ws: WebSocket) -> None:
    await ws.accept()
    try:
        data = await ws.receive_json()
        payload = GenerateChapterRequest(**data)
    except Exception:  # noqa: BLE001 — 参数解析/校验失败统一回错
        await ws.send_json({"stage": "error", "message": "无效的请求参数"})
        await ws.close()
        return

    async def on_progress(event: dict) -> None:
        await ws.send_json(event)

    try:
        result = await GenerationPipeline().generate(
            novel_id=payload.novel_id,
            chapter_number=payload.chapter_number,
            outline=payload.outline,
            target_word_count=payload.target_word_count,
            on_progress=on_progress,
        )
        await ws.send_json(
            {
                "stage": "complete",
                "chapter_id": str(result["chapter_id"]),
                "word_count": result["word_count"],
            }
        )
    except WebSocketDisconnect:
        return
    except Exception as exc:  # noqa: BLE001 — 把生成错误回传给客户端
        await ws.send_json({"stage": "error", "message": str(exc)})
    finally:
        await ws.close()
