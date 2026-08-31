// 后端接口的 snake_case 类型，直接照搬后端 schema，勿转 camelCase（否则字段对不上）。

export interface Novel {
  id: string
  title: string
  genre?: string | null
  synopsis?: string | null
  notes?: string | null
  created_at: string
  updated_at: string
}

export interface Character {
  id: string
  novel_id: string
  name: string
  aliases?: string[] | null
  role?: string | null
  personality?: string | null
  background?: string | null
  appearance?: string | null
  goals?: string | null
  relationships?: Record<string, string> | null
  notes?: string | null
  created_at: string
  updated_at: string
}

export interface WorldSetting {
  id: string
  novel_id: string
  category: string
  name: string
  description?: string | null
  parent_id?: string | null
  notes?: string | null
  created_at: string
  updated_at: string
}

export interface TimelineEvent {
  id: string
  novel_id: string
  title: string
  description?: string | null
  time_point?: string | null
  order_index: number
  status: string
  chapter_id?: string | null
  involved_character_ids?: string[] | null
  created_at: string
  updated_at: string
}

export interface Chapter {
  id: string
  novel_id: string
  number: number
  title?: string | null
  summary?: string | null
  outline?: string | null
  content?: string | null
  word_count: number
  status: string
  created_at: string
  updated_at: string
}

export interface Draft {
  id: string
  chapter_id: string
  version: number
  content: string
  note?: string | null
  created_at: string
  updated_at: string
}

export interface DraftDiff {
  from_version: number
  to_version: number
  diff: string[]
}

export interface ReviewReport {
  issues: string[]
  conflicts: string[]
  fixed: boolean
  summary?: string | null
}

export interface GenerateResponse {
  chapter_id: string
  content: string
  word_count: number
  review?: ReviewReport | null
}

export interface GenerateChapterRequest {
  novel_id: string
  chapter_number: number
  outline?: string | null
  target_word_count: number
}

export interface GenerateChaptersRequest {
  novel_id: string
  start_chapter: number
  count: number
  target_word_count: number
  outlines?: (string | null)[] | null
}

export interface ProgressEvent {
  stage: string
  chapter?: number
  round?: number
  chapter_id?: string
  word_count?: number
  message?: string
}
