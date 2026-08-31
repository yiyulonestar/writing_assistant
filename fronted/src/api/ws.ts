import type { GenerateChapterRequest, GenerateResponse, ProgressEvent } from './types'

// 生成进度 WebSocket：连接后先发送请求体，服务端边生成边推 stage 事件。
// 注意：/generate/ws 只回传进度与 chapter_id / word_count，不回传正文；
// 需要正文时，拿到 chapter_id 后再 GET /chapters/{id} 拉取。
export function generateWithProgress(
  payload: GenerateChapterRequest,
  onProgress: (e: ProgressEvent) => void,
): Promise<GenerateResponse> {
  return new Promise((resolve, reject) => {
    const proto = location.protocol === 'https:' ? 'wss://' : 'ws://'
    const ws = new WebSocket(`${proto}${location.host}/api/v1/generate/ws`)

    ws.onopen = () => ws.send(JSON.stringify(payload))
    ws.onmessage = (msg) => {
      const e = JSON.parse(msg.data) as ProgressEvent
      if (e.stage === 'complete') {
        resolve({ chapter_id: e.chapter_id ?? '', content: '', word_count: e.word_count ?? 0 })
      } else if (e.stage === 'error') {
        reject(new Error(e.message || '生成失败'))
      } else {
        onProgress(e)
      }
    }
    ws.onerror = () => reject(new Error('WebSocket 连接失败'))
  })
}
