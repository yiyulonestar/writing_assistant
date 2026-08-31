<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { api } from '../api/client'
import type { Chapter, Draft, DraftDiff } from '../api/types'
import { toast } from '../toast'
import Modal from '../components/Modal.vue'
import DiffView from '../components/DiffView.vue'

const props = defineProps<{ chapterId: string }>()

const chapter = ref<Chapter | null>(null)
const loading = ref(false)
const saving = ref(false)

const form = reactive({ title: '', status: 'draft', outline: '', summary: '', content: '' })

const statusText: Record<string, string> = { draft: '草稿', revising: '修改中', done: '已完成' }

// 草稿版本历史
const drafts = ref<Draft[]>([])
const draftsLoading = ref(false)
const showDrafts = ref(false)
const diffBase = ref<number | ''>('')
const diffTarget = ref<number | ''>('')
const diff = ref<DraftDiff | null>(null)
const diffLoading = ref(false)

const savingDraft = ref(false)
const draftNote = ref('')

// 局部重写
const showRewrite = ref(false)
const rewriteInstruction = ref('')
const rewriteStart = ref(-1)
const rewriteEnd = ref(-1)
const rewriting = ref(false)

async function load() {
  loading.value = true
  try {
    chapter.value = await api.get<Chapter>(`/chapters/${props.chapterId}`)
    form.title = chapter.value.title ?? ''
    form.status = chapter.value.status
    form.outline = chapter.value.outline ?? ''
    form.summary = chapter.value.summary ?? ''
    form.content = chapter.value.content ?? ''
  } catch (e) {
    toast((e as Error).message, 'error')
  } finally {
    loading.value = false
  }
}

// 实时字数：与后端一致，按中文字符计
const liveWordCount = computed(() => countCjk(form.content))

function countCjk(text: string): number {
  return text.match(/[一-鿿]/g)?.length ?? 0
}

async function save() {
  saving.value = true
  try {
    const updated = await api.patch<Chapter>(`/chapters/${props.chapterId}`, {
      title: form.title.trim() || null,
      status: form.status,
      outline: form.outline || null,
      summary: form.summary || null,
      content: form.content,
    })
    chapter.value = updated
    toast('已保存', 'success')
  } catch (e) {
    toast((e as Error).message, 'error')
  } finally {
    saving.value = false
  }
}

async function loadDrafts() {
  draftsLoading.value = true
  try {
    drafts.value = await api.get<Draft[]>(`/chapters/${props.chapterId}/drafts`)
    if (drafts.value.length) {
      const last = drafts.value[drafts.value.length - 1].version
      const prev = drafts.value.length > 1 ? drafts.value[drafts.value.length - 2].version : last
      diffTarget.value = last
      diffBase.value = prev
      await loadDiff()
    } else {
      diff.value = null
    }
  } catch (e) {
    toast((e as Error).message, 'error')
  } finally {
    draftsLoading.value = false
  }
}

function openDrafts() {
  showDrafts.value = true
  loadDrafts()
}

async function loadDiff() {
  if (diffBase.value === '' || diffTarget.value === '') {
    diff.value = null
    return
  }
  if (diffBase.value === diffTarget.value) {
    diff.value = { from_version: diffBase.value, to_version: diffTarget.value, diff: [] }
    return
  }
  diffLoading.value = true
  try {
    diff.value = await api.get<DraftDiff>(
      `/chapters/${props.chapterId}/drafts/${diffTarget.value}/diff?base=${diffBase.value}`,
    )
  } catch (e) {
    toast((e as Error).message, 'error')
  } finally {
    diffLoading.value = false
  }
}

async function saveDraft() {
  if (!form.content.trim()) {
    toast('正文为空，无需保存草稿', 'error')
    return
  }
  savingDraft.value = true
  try {
    await api.post(`/chapters/${props.chapterId}/drafts`, {
      content: form.content,
      note: draftNote.value.trim() || null,
    })
    toast('已保存草稿', 'success')
    draftNote.value = ''
  } catch (e) {
    toast((e as Error).message, 'error')
  } finally {
    savingDraft.value = false
  }
}

function fmt(s: string) {
  return new Date(s).toLocaleString('zh-CN', { hour12: false })
}

// 与后端 _split_paragraphs 保持一致：按空行分段、strip、过滤空段
function splitParagraphs(content: string): string[] {
  return content
    .split('\n\n')
    .map((p) => p.trim())
    .filter(Boolean)
}

const paragraphs = computed(() => splitParagraphs(form.content))

function openRewrite() {
  if (!form.content.trim()) {
    toast('章节暂无正文，无法重写', 'error')
    return
  }
  rewriteInstruction.value = ''
  rewriteStart.value = -1
  rewriteEnd.value = -1
  showRewrite.value = true
}

function onParaClick(i: number) {
  if (rewriteStart.value === -1) {
    rewriteStart.value = i
    rewriteEnd.value = i
  } else if (i < rewriteStart.value) {
    rewriteStart.value = i
  } else if (i > rewriteEnd.value) {
    rewriteEnd.value = i
  } else {
    rewriteStart.value = i
    rewriteEnd.value = i
  }
}

async function doRewrite() {
  const s = Number(rewriteStart.value)
  const e = Number(rewriteEnd.value)
  const len = paragraphs.value.length
  if (!Number.isInteger(s) || !Number.isInteger(e) || s < 0 || e < s || e >= len) {
    toast('请选择合法的段落范围', 'error')
    return
  }
  rewriting.value = true
  try {
    const updated = await api.post<Chapter>(`/chapters/${props.chapterId}/rewrite`, {
      start: s,
      end: e,
      instruction: rewriteInstruction.value.trim() || null,
    })
    chapter.value = updated
    form.content = updated.content ?? ''
    toast('重写完成，已生成新草稿版本', 'success')
    showRewrite.value = false
  } catch (err) {
    toast((err as Error).message, 'error')
  } finally {
    rewriting.value = false
  }
}

onMounted(load)
</script>

<template>
  <div>
    <div v-if="loading" class="empty">加载中…</div>

    <div v-else-if="chapter" class="editor">
      <div class="editor__meta">
        <div class="field editor__title">
          <label>标题</label>
          <input v-model="form.title" placeholder="章节标题" />
        </div>
        <div class="field editor__status">
          <label>状态</label>
          <select v-model="form.status">
            <option value="draft">草稿</option>
            <option value="revising">修改中</option>
            <option value="done">已完成</option>
          </select>
        </div>
        <div class="field editor__count">
          <label>字数</label>
          <div class="editor__count-value">{{ liveWordCount }} 字</div>
        </div>
        <div class="editor__actions">
          <button class="btn btn--primary" :disabled="saving" @click="save">
            {{ saving ? '保存中…' : '保存' }}
          </button>
          <button class="btn" :disabled="savingDraft" @click="saveDraft">
            {{ savingDraft ? '保存中…' : '保存草稿' }}
          </button>
          <button class="btn btn--ghost" @click="openRewrite">局部重写</button>
          <button class="btn btn--ghost" @click="openDrafts">版本历史</button>
        </div>
      </div>

      <div class="editor__grid">
        <div class="field">
          <label>正文</label>
          <textarea
            v-model="form.content"
            class="editor__content"
            placeholder="在此写作正文，或从「生成」面板生成后回来编辑…"
          ></textarea>
        </div>

        <div class="editor__side">
          <div class="field">
            <label>大纲</label>
            <textarea v-model="form.outline" rows="6" placeholder="本章大纲 / 目标"></textarea>
          </div>
          <div class="field">
            <label>摘要</label>
            <textarea v-model="form.summary" rows="4" placeholder="本章摘要"></textarea>
          </div>
        </div>
      </div>
    </div>

    <!-- 版本历史弹窗 -->
    <Modal :open="showDrafts" title="版本历史" width="720px" @close="showDrafts = false">
      <div v-if="draftsLoading" class="muted">加载中…</div>
      <div v-else-if="drafts.length === 0" class="muted">还没有草稿版本。</div>
      <div v-else>
        <div class="draft-controls">
          <div class="field">
            <label>基准版本</label>
            <select v-model="diffBase" @change="loadDiff">
              <option v-for="d in drafts" :key="d.version" :value="d.version">v{{ d.version }}</option>
            </select>
          </div>
          <div class="field">
            <label>对比版本</label>
            <select v-model="diffTarget" @change="loadDiff">
              <option v-for="d in drafts" :key="d.version" :value="d.version">v{{ d.version }}</option>
            </select>
          </div>
        </div>

        <div class="draft-list">
          <div v-for="d in drafts" :key="d.version" class="draft-item">
            <span class="draft-item__version">v{{ d.version }}</span>
            <span class="draft-item__note">{{ d.note || '（无说明）' }}</span>
            <span class="draft-item__time muted">{{ fmt(d.created_at) }}</span>
          </div>
        </div>

        <div class="draft-diff">
          <div class="draft-diff__title">
            差异对比：v{{ diffBase }} → v{{ diffTarget }}
            <span v-if="diffLoading" class="muted">加载中…</span>
          </div>
          <DiffView v-if="diff" :lines="diff.diff" />
        </div>
      </div>
      <template #footer>
        <button class="btn" @click="showDrafts = false">关闭</button>
      </template>
    </Modal>

    <!-- 局部重写弹窗 -->
    <Modal :open="showRewrite" title="局部重写" width="720px" @close="showRewrite = false">
      <div class="form">
        <div class="field">
          <label>重写指令（可选）</label>
          <textarea
            v-model="rewriteInstruction"
            rows="2"
            placeholder="如：改成更紧张的节奏 / 补充打斗细节"
          ></textarea>
        </div>
        <div class="rewrite-range">
          <div class="field">
            <label>起始段</label>
            <input v-model.number="rewriteStart" type="number" :min="0" :max="paragraphs.length - 1" />
          </div>
          <div class="field">
            <label>结束段</label>
            <input v-model.number="rewriteEnd" type="number" :min="0" :max="paragraphs.length - 1" />
          </div>
        </div>
        <div class="field">
          <label>选择重写段落（点击设置范围，共 {{ paragraphs.length }} 段，按空行分隔）</label>
          <div class="rewrite-paras">
            <div
              v-for="(p, i) in paragraphs"
              :key="i"
              class="rewrite-para"
              :class="{ 'rewrite-para--selected': i >= rewriteStart && i <= rewriteEnd }"
              @click="onParaClick(i)"
            >
              <span class="rewrite-para__idx">{{ i }}</span>
              <span class="rewrite-para__text">{{ p }}</span>
            </div>
          </div>
        </div>
      </div>
      <template #footer>
        <button class="btn" @click="showRewrite = false">取消</button>
        <button class="btn btn--primary" :disabled="rewriting" @click="doRewrite">
          {{ rewriting ? '重写中…' : '开始重写' }}
        </button>
      </template>
    </Modal>
  </div>
</template>
