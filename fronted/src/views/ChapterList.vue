<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { api } from '../api/client'
import type { Chapter } from '../api/types'
import { store } from '../store'
import { toast } from '../toast'
import Modal from '../components/Modal.vue'
import ConfirmDialog from '../components/ConfirmDialog.vue'
import ChapterEditor from './ChapterEditor.vue'

const props = defineProps<{ novelId: string }>()

const list = ref<Chapter[]>([])
const loading = ref(false)

const showForm = ref(false)
const saving = ref(false)
const form = reactive({ number: 1, title: '' })

const deleting = ref<Chapter | null>(null)
const deletingLoading = ref(false)

const statusText: Record<string, string> = { draft: '草稿', revising: '修改中', done: '已完成' }

async function load() {
  loading.value = true
  try {
    list.value = await api.get<Chapter[]>(`/chapters?novel_id=${props.novelId}`)
  } catch (e) {
    toast((e as Error).message, 'error')
  } finally {
    loading.value = false
  }
}

function openCreate() {
  form.number = list.value.length ? Math.max(...list.value.map((c) => c.number)) + 1 : 1
  form.title = ''
  showForm.value = true
}

async function submit() {
  if (!form.number) {
    toast('请填写章节号', 'error')
    return
  }
  saving.value = true
  try {
    const created = await api.post<Chapter>('/chapters', {
      novel_id: props.novelId,
      number: Number(form.number),
      title: form.title.trim() || null,
    })
    toast('已创建', 'success')
    showForm.value = false
    await load()
    store.currentChapterId = created.id
  } catch (e) {
    toast((e as Error).message, 'error')
  } finally {
    saving.value = false
  }
}

function requestDelete(c: Chapter) {
  deleting.value = c
}

async function doDelete() {
  if (!deleting.value) return
  const id = deleting.value.id
  deletingLoading.value = true
  try {
    await api.del(`/chapters/${id}`)
    toast('已删除', 'success')
    deleting.value = null
    if (store.currentChapterId === id) store.currentChapterId = ''
    await load()
  } catch (e) {
    toast((e as Error).message, 'error')
  } finally {
    deletingLoading.value = false
  }
}

onMounted(load)
</script>

<template>
  <div class="view">
    <template v-if="store.currentChapterId">
      <div class="toolbar">
        <button class="btn btn--ghost" @click="store.currentChapterId = ''">← 返回章节列表</button>
      </div>
      <ChapterEditor :chapter-id="store.currentChapterId" />
    </template>

    <template v-else>
      <div class="toolbar">
        <h2>章节列表</h2>
        <button class="btn btn--primary" @click="openCreate">＋ 新建章节</button>
      </div>

      <div v-if="loading" class="empty">加载中…</div>
      <div v-else-if="list.length === 0" class="empty">
        <p>还没有章节，点击「新建章节」手动创建，或前往「生成」一键生成。</p>
      </div>
      <div v-else class="list">
        <div v-for="c in list" :key="c.id" class="list-item">
          <div class="list-item__main">
            <div class="list-item__title">
              <span class="muted">第 {{ c.number }} 章</span>
              {{ c.title || '（无标题）' }}
              <span class="badge">{{ statusText[c.status] ?? c.status }}</span>
            </div>
            <div class="muted">字数：{{ c.word_count }}</div>
            <div v-if="c.summary" class="muted line-clamp">{{ c.summary }}</div>
          </div>
          <div class="list-item__actions">
            <button class="btn btn--primary btn--sm" @click="store.currentChapterId = c.id">
              打开
            </button>
            <button class="btn btn--danger btn--sm" @click="requestDelete(c)">删除</button>
          </div>
        </div>
      </div>

      <Modal :open="showForm" title="新建章节" @close="showForm = false">
        <div class="form">
          <div class="field">
            <label>章节号 <span class="req">*</span></label>
            <input v-model.number="form.number" type="number" />
          </div>
          <div class="field">
            <label>标题</label>
            <input v-model="form.title" placeholder="可选" />
          </div>
        </div>
        <template #footer>
          <button class="btn" @click="showForm = false">取消</button>
          <button class="btn btn--primary" :disabled="saving" @click="submit">
            {{ saving ? '创建中…' : '创建' }}
          </button>
        </template>
      </Modal>

      <ConfirmDialog
        :open="!!deleting"
        title="删除章节"
        :message="deleting ? `确认删除第 ${deleting.number} 章${deleting.title ? `（${deleting.title}）` : ''}？其草稿版本将一并删除。` : ''"
        :loading="deletingLoading"
        @confirm="doDelete"
        @cancel="deleting = null"
      />
    </template>
  </div>
</template>
