<script setup lang="ts">
import { onBeforeUnmount, onMounted, reactive, ref } from 'vue'
import { api } from '../api/client'
import { generateWithProgress } from '../api/ws'
import type { Chapter, GenerateResponse, ProgressEvent } from '../api/types'
import { openChapter } from '../store'
import { toast } from '../toast'
import ProgressSteps from '../components/ProgressSteps.vue'
import ReviewCard from '../components/ReviewCard.vue'

const props = defineProps<{ novelId: string }>()

const tab = ref<'single' | 'batch'>('single')

// ---- 单章 ----
const singleForm = reactive({ chapter_number: 1, target_word_count: 3000, outline: '' })
// http：返回正文 + 审稿报告；ws：实时进度（无审稿报告，需完成后回拉正文）
const singleMode = ref<'http' | 'ws'>('http')
const singleResult = ref<GenerateResponse | null>(null)

// ---- 批量 ----
const batchForm = reactive({ start_chapter: 1, count: 3, target_word_count: 3000, outlines: '' })
const batchResults = ref<GenerateResponse[]>([])

// ---- 运行状态 ----
const running = ref(false)
const stage = ref('')
const elapsed = ref(0)
let timer: number | undefined

function startTimer() {
  elapsed.value = 0
  timer = window.setInterval(() => {
    elapsed.value++
  }, 1000)
}

function stopTimer() {
  if (timer) {
    clearInterval(timer)
    timer = undefined
  }
}

onBeforeUnmount(stopTimer)

function fmtElapsed(s: number) {
  const m = Math.floor(s / 60)
  const sec = s % 60
  return `${m}:${String(sec).padStart(2, '0')}`
}

async function initChapterNumbers() {
  try {
    const chapters = await api.get<Chapter[]>(`/chapters?novel_id=${props.novelId}`)
    const max = chapters.length ? Math.max(...chapters.map((c) => c.number)) : 0
    singleForm.chapter_number = max + 1
    batchForm.start_chapter = max + 1
  } catch {
    /* 忽略：后端未启动时用户可手填 */
  }
}

onMounted(initChapterNumbers)

async function runSingle() {
  if (running.value) return
  running.value = true
  stage.value = ''
  singleResult.value = null

  const payload = {
    novel_id: props.novelId,
    chapter_number: Number(singleForm.chapter_number) || 1,
    target_word_count: Number(singleForm.target_word_count) || 3000,
    outline: singleForm.outline.trim() || null,
  }

  startTimer()
  try {
    if (singleMode.value === 'ws') {
      const res = await generateWithProgress(payload, (e: ProgressEvent) => {
        stage.value = e.stage
      })
      stage.value = 'complete'
      // WS 不回传正文与审稿报告，按 chapter_id 回拉正文
      const ch = await api.get<Chapter>(`/chapters/${res.chapter_id}`)
      singleResult.value = {
        chapter_id: res.chapter_id,
        content: ch.content ?? '',
        word_count: res.word_count,
        review: null,
      }
    } else {
      singleResult.value = await api.post<GenerateResponse>('/generate/chapter', payload)
      stage.value = 'done'
    }
    toast('生成完成', 'success')
  } catch (e) {
    toast((e as Error).message, 'error')
  } finally {
    stopTimer()
    running.value = false
  }
}

async function runBatch() {
  if (running.value) return
  running.value = true
  batchResults.value = []

  const count = Number(batchForm.count) || 1
  const outlines = batchForm.outlines.trim()
    ? batchForm.outlines
        .split('\n')
        .map((s) => s.trim())
        .filter(Boolean)
    : null

  const payload = {
    novel_id: props.novelId,
    start_chapter: Number(batchForm.start_chapter) || 1,
    count,
    target_word_count: Number(batchForm.target_word_count) || 3000,
    outlines,
  }

  startTimer()
  try {
    batchResults.value = await api.post<GenerateResponse[]>('/generate/batch', payload)
    toast(`批量生成完成，共 ${batchResults.value.length} 章`, 'success')
  } catch (e) {
    toast((e as Error).message, 'error')
  } finally {
    stopTimer()
    running.value = false
  }
}

async function copyText(text: string) {
  try {
    await navigator.clipboard.writeText(text)
    toast('已复制到剪贴板', 'success')
  } catch {
    toast('复制失败', 'error')
  }
}
</script>

<template>
  <div class="view">
    <div class="tabs">
      <button class="tab" :class="{ 'tab--active': tab === 'single' }" @click="tab = 'single'">
        单章生成
      </button>
      <button class="tab" :class="{ 'tab--active': tab === 'batch' }" @click="tab = 'batch'">
        批量生成
      </button>
    </div>

    <!-- ===== 单章 ===== -->
    <div v-if="tab === 'single'" class="gen-panel">
      <div class="form">
        <div class="gen-row">
          <div class="field">
            <label>章节号</label>
            <input v-model.number="singleForm.chapter_number" type="number" />
          </div>
          <div class="field">
            <label>目标字数</label>
            <input v-model.number="singleForm.target_word_count" type="number" />
          </div>
        </div>
        <div class="field">
          <label>本章大纲（可选）</label>
          <textarea v-model="singleForm.outline" rows="3" placeholder="留空则自动拆解章节目标"></textarea>
        </div>
        <div class="field">
          <label>生成方式</label>
          <div class="radio-row">
            <label class="radio">
              <input v-model="singleMode" type="radio" value="http" />
              完整模式（返回正文 + 审稿报告）
            </label>
            <label class="radio">
              <input v-model="singleMode" type="radio" value="ws" />
              实时进度（WebSocket，无审稿报告）
            </label>
          </div>
        </div>
        <div>
          <button class="btn btn--primary" :disabled="running" @click="runSingle">
            {{ running ? '生成中…' : '开始生成' }}
          </button>
        </div>
      </div>

      <!-- 进度 / 结果 -->
      <div v-if="running" class="gen-progress">
        <ProgressSteps v-if="singleMode === 'ws'" :stage="stage" />
        <div v-else class="gen-progress__spinner">
          <span class="spinner"></span>
          <span>正在生成（通常需要 1~3 分钟）… 已用 {{ fmtElapsed(elapsed) }}</span>
        </div>
      </div>

      <div v-else-if="singleResult" class="gen-result">
        <div class="gen-result__head">
          <h3>生成结果（第 {{ singleForm.chapter_number }} 章）</h3>
          <div class="gen-result__actions">
            <span class="muted">{{ singleResult.word_count }} 字</span>
            <button class="btn btn--sm" @click="copyText(singleResult.content)">复制正文</button>
            <button class="btn btn--primary btn--sm" @click="openChapter(singleResult.chapter_id)">
              去章节编辑
            </button>
          </div>
        </div>

        <ReviewCard :review="singleResult.review" />
        <p v-if="singleResult.review === null" class="muted">
          当前为「实时进度」模式，审稿报告仅在「完整模式」下返回。
        </p>

        <div class="content-preview">{{ singleResult.content }}</div>
      </div>
    </div>

    <!-- ===== 批量 ===== -->
    <div v-else class="gen-panel">
      <div class="form">
        <div class="gen-row">
          <div class="field">
            <label>起始章节号</label>
            <input v-model.number="batchForm.start_chapter" type="number" />
          </div>
          <div class="field">
            <label>章节数</label>
            <input v-model.number="batchForm.count" type="number" />
          </div>
          <div class="field">
            <label>目标字数（每章）</label>
            <input v-model.number="batchForm.target_word_count" type="number" />
          </div>
        </div>
        <div class="field">
          <label>各章大纲（可选，每行一章，按顺序对应）</label>
          <textarea
            v-model="batchForm.outlines"
            rows="4"
            placeholder="第一章大纲&#10;第二章大纲&#10;…"
          ></textarea>
        </div>
        <div>
          <button class="btn btn--primary" :disabled="running" @click="runBatch">
            {{ running ? '生成中…' : '开始批量生成' }}
          </button>
        </div>
      </div>

      <div v-if="running" class="gen-progress">
        <span class="spinner"></span>
        <span>正在批量生成 {{ batchForm.count }} 章（串行）… 已用 {{ fmtElapsed(elapsed) }}</span>
      </div>

      <div v-if="batchResults.length" class="gen-result">
        <div
          v-for="(r, i) in batchResults"
          :key="r.chapter_id"
          class="batch-item"
        >
          <div class="gen-result__head">
            <h3>第 {{ batchForm.start_chapter + i }} 章</h3>
            <div class="gen-result__actions">
              <span class="muted">{{ r.word_count }} 字</span>
              <button class="btn btn--sm" @click="copyText(r.content)">复制正文</button>
              <button class="btn btn--primary btn--sm" @click="openChapter(r.chapter_id)">去章节编辑</button>
            </div>
          </div>
          <ReviewCard :review="r.review" />
          <details class="content-toggle">
            <summary>查看正文</summary>
            <div class="content-preview">{{ r.content }}</div>
          </details>
        </div>
      </div>
    </div>
  </div>
</template>
