// fetch 封装：统一 baseURL、鉴权头、JSON 处理与错误抛出。
// 约定：PATCH 用「完整可编辑字段 + 空值置 null」发送（null 会清空该字段，符合后端 exclude_unset 语义），
// 因此编辑表单需把现有字段全部回填，避免空值误清已有数据。

// 开发期走 Vite 代理（相对路径）；直连后端时改为 'http://localhost:8000/api/v1'
const BASE = '/api/v1'

// 后端 .env 若配置 API_KEY，则生成类接口需 X-API-Key；填在此处统一附加（带在 CRUD 上无害）
const API_KEY = ''

async function request<T>(method: string, path: string, body?: unknown): Promise<T> {
  const headers: Record<string, string> = {}
  if (body !== undefined) headers['Content-Type'] = 'application/json'
  if (API_KEY) headers['X-API-Key'] = API_KEY

  const res = await fetch(BASE + path, {
    method,
    headers,
    body: body === undefined ? undefined : JSON.stringify(body),
  })

  // DELETE 成功返回 204 No Content，先判断再解析，否则 res.json() 会抛错
  if (res.status === 204) return undefined as T

  const data = await res.json().catch(() => ({}))
  if (!res.ok) throw new Error((data as { detail?: string }).detail || `HTTP ${res.status}`)
  return data as T
}

export const api = {
  get: <T>(p: string) => request<T>('GET', p),
  post: <T>(p: string, b?: unknown) => request<T>('POST', p, b),
  patch: <T>(p: string, b: unknown) => request<T>('PATCH', p, b),
  del: <T>(p: string) => request<T>('DELETE', p),
}
