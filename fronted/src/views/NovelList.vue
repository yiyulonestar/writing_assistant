<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { api } from '../api/client'
import type { Novel } from '../api/types'
import { selectNovel } from '../store'
import { toast } from '../toast'
import Modal from '../components/Modal.vue'
import ConfirmDialog from '../components/ConfirmDialog.vue'

const novels = ref<Novel[]>([])
const loading = ref(false)

const showForm = ref(false)
const editing = ref<Novel | null>(null)
const saving = ref(false)
const form = reactive({ title: '', genre: '', synopsis: '', notes: '' })

const deleting = ref<Novel | null>(null)
const deletingLoading = ref(false)

async function load() {
  loading.value = true
  try {
    novels.value = await api.get<Novel[]>('/novels')
  } catch (e) {
    toast((e as Error).message, 'error')
  } finally {
    loading.value = false
  }
}

function openCreate() {
  editing.value = null
  form.title = ''
  form.genre = ''
  form.synopsis = ''
  form.notes = ''
  showForm.value = true
}

function openEdit(n: Novel) {
  editing.value = n
  form.title = n.title
  form.genre = n.genre ?? ''
  form.synopsis = n.synopsis ?? ''
  form.notes = n.notes ?? ''
  showForm.value = true
}

function buildPayload() {
  return {
    title: form.title,
    genre: form.genre.trim() || null,
    synopsis: form.synopsis.trim() || null,
    notes: form.notes.trim() || null,
  }
}

async function submit() {
  if (!form.title.trim()) {
    toast('请填写小说标题', 'error')
    return
  }
  saving.value = true
  try {
    if (editing.value) {
      await api.patch(`/novels/${editing.value.id}`, buildPayload())
      toast('已更新', 'success')
    } else {
      await api.post('/novels', buildPayload())
      toast('已创建', 'success')
    }
    showForm.value = false
    await load()
  } catch (e) {
    toast((e as Error).message, 'error')
  } finally {
    saving.value = false
  }
}

function requestDelete(n: Novel) {
  deleting.value = n
}

async function doDelete() {
  if (!deleting.value) return
  deletingLoading.value = true
  try {
    await api.del(`/novels/${deleting.value.id}`)
    toast('已删除', 'success')
    deleting.value = null
    await load()
  } catch (e) {
    toast((e as Error).message, 'error')
  } finally {
    deletingLoading.value = false
  }
}

function enter(n: Novel) {
  selectNovel(n.id, n.title)
}

function fmt(s: string) {
  return new Date(s).toLocaleString('zh-CN', { hour12: false })
}

onMounted(load)
</script>

<template>
  <div class="view">
    <div class="toolbar">
      <h2>小说列表</h2>
      <button class="btn btn--primary" @click="openCreate">＋ 新建小说</button>
    </div>

    <div v-if="loading" class="empty">加载中…</div>
    <div v-else-if="novels.length === 0" class="empty">
      <p>还没有小说，点击「新建小说」开始。</p>
    </div>
    <div v-else class="novel-grid">
      <div v-for="n in novels" :key="n.id" class="novel-card">
        <div class="novel-card__head">
          <h3 class="novel-card__title">{{ n.title }}</h3>
          <span v-if="n.genre" class="badge">{{ n.genre }}</span>
        </div>
        <p v-if="n.synopsis" class="novel-card__synopsis">{{ n.synopsis }}</p>
        <div class="novel-card__meta muted">更新于 {{ fmt(n.updated_at) }}</div>
        <div class="novel-card__actions">
          <button class="btn btn--primary btn--sm" @click="enter(n)">进入</button>
          <button class="btn btn--ghost btn--sm" @click="openEdit(n)">编辑</button>
          <button class="btn btn--danger btn--sm" @click="requestDelete(n)">删除</button>
        </div>
      </div>
    </div>

    <Modal :open="showForm" :title="editing ? '编辑小说' : '新建小说'" @close="showForm = false">
      <div class="form">
        <div class="field">
          <label>标题 <span class="req">*</span></label>
          <input v-model="form.title" placeholder="小说标题" />
        </div>
        <div class="field">
          <label>题材</label>
          <input v-model="form.genre" placeholder="如：玄幻 / 都市 / 科幻" />
        </div>
        <div class="field">
          <label>简介</label>
          <textarea v-model="form.synopsis" rows="3" placeholder="故事简介"></textarea>
        </div>
        <div class="field">
          <label>备注</label>
          <textarea v-model="form.notes" rows="2" placeholder="备注"></textarea>
        </div>
      </div>
      <template #footer>
        <button class="btn" @click="showForm = false">取消</button>
        <button class="btn btn--primary" :disabled="saving" @click="submit">
          {{ saving ? '保存中…' : '保存' }}
        </button>
      </template>
    </Modal>

    <ConfirmDialog
      :open="!!deleting"
      title="删除小说"
      :message="
        deleting
          ? `确认删除《${deleting.title}》？将级联删除其角色、章节、时间线、世界观等所有数据，且不可恢复。`
          : ''
      "
      :loading="deletingLoading"
      @confirm="doDelete"
      @cancel="deleting = null"
    />
  </div>
</template>
