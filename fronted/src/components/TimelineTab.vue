<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { api } from '../api/client'
import type { Character, TimelineEvent } from '../api/types'
import { toast } from '../toast'
import Modal from './Modal.vue'
import ConfirmDialog from './ConfirmDialog.vue'

const props = defineProps<{ novelId: string }>()

const list = ref<TimelineEvent[]>([])
const characters = ref<Character[]>([])
const loading = ref(false)

const showForm = ref(false)
const editing = ref<TimelineEvent | null>(null)
const saving = ref(false)
const form = reactive({
  title: '',
  description: '',
  time_point: '',
  order_index: 0,
  status: 'planned',
  involved: [] as string[],
})

const deleting = ref<TimelineEvent | null>(null)
const deletingLoading = ref(false)

async function load() {
  loading.value = true
  try {
    const [events, chars] = await Promise.all([
      api.get<TimelineEvent[]>(`/timeline?novel_id=${props.novelId}`),
      api.get<Character[]>(`/characters?novel_id=${props.novelId}`),
    ])
    list.value = events
    characters.value = chars
  } catch (e) {
    toast((e as Error).message, 'error')
  } finally {
    loading.value = false
  }
}

function openCreate() {
  editing.value = null
  form.title = ''
  form.description = ''
  form.time_point = ''
  form.order_index = list.value.length
  form.status = 'planned'
  form.involved = []
  showForm.value = true
}

function openEdit(t: TimelineEvent) {
  editing.value = t
  form.title = t.title
  form.description = t.description ?? ''
  form.time_point = t.time_point ?? ''
  form.order_index = t.order_index
  form.status = t.status
  form.involved = t.involved_character_ids ?? []
  showForm.value = true
}

function buildPayload() {
  return {
    title: form.title,
    description: form.description.trim() || null,
    time_point: form.time_point.trim() || null,
    order_index: Number(form.order_index) || 0,
    status: form.status,
    involved_character_ids: form.involved.length ? form.involved : null,
  }
}

async function submit() {
  if (!form.title.trim()) {
    toast('请填写事件标题', 'error')
    return
  }
  saving.value = true
  try {
    if (editing.value) {
      await api.patch(`/timeline/${editing.value.id}`, buildPayload())
      toast('已更新', 'success')
    } else {
      await api.post('/timeline', { novel_id: props.novelId, ...buildPayload() })
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

function requestDelete(t: TimelineEvent) {
  deleting.value = t
}

async function doDelete() {
  if (!deleting.value) return
  deletingLoading.value = true
  try {
    await api.del(`/timeline/${deleting.value.id}`)
    toast('已删除', 'success')
    deleting.value = null
    await load()
  } catch (e) {
    toast((e as Error).message, 'error')
  } finally {
    deletingLoading.value = false
  }
}

function charName(id: string): string {
  return characters.value.find((c) => c.id === id)?.name ?? id
}

const statusText: Record<string, string> = {
  planned: '计划中',
  occurred: '已发生',
}

onMounted(load)
</script>

<template>
  <div>
    <div class="toolbar">
      <span class="muted">共 {{ list.length }} 个事件</span>
      <button class="btn btn--primary" @click="openCreate">＋ 新建事件</button>
    </div>

    <div v-if="loading" class="empty">加载中…</div>
    <div v-else-if="list.length === 0" class="empty">
      <p>还没有时间线事件，点击「新建事件」添加。</p>
    </div>
    <div v-else class="list">
      <div v-for="t in list" :key="t.id" class="list-item">
        <div class="list-item__main">
          <div class="list-item__title">
            <span class="muted">{{ t.order_index }}</span>
            {{ t.title }}
            <span class="badge" :class="`badge--${t.status}`">{{ statusText[t.status] ?? t.status }}</span>
          </div>
          <div v-if="t.time_point" class="muted">时间点：{{ t.time_point }}</div>
          <div
            v-if="t.involved_character_ids && t.involved_character_ids.length"
            class="muted"
          >
            涉及角色：{{ t.involved_character_ids.map(charName).join('、') }}
          </div>
          <div v-if="t.description" class="muted line-clamp">{{ t.description }}</div>
        </div>
        <div class="list-item__actions">
          <button class="btn btn--ghost btn--sm" @click="openEdit(t)">编辑</button>
          <button class="btn btn--danger btn--sm" @click="requestDelete(t)">删除</button>
        </div>
      </div>
    </div>

    <Modal :open="showForm" :title="editing ? '编辑事件' : '新建事件'" @close="showForm = false">
      <div class="form">
        <div class="field">
          <label>标题 <span class="req">*</span></label>
          <input v-model="form.title" placeholder="事件标题" />
        </div>
        <div class="field">
          <label>时间点</label>
          <input v-model="form.time_point" placeholder="如：第一章之前 / 三年前" />
        </div>
        <div class="field">
          <label>排序序号</label>
          <input v-model.number="form.order_index" type="number" />
        </div>
        <div class="field">
          <label>状态</label>
          <select v-model="form.status">
            <option value="planned">计划中</option>
            <option value="occurred">已发生</option>
          </select>
        </div>
        <div class="field">
          <label>描述</label>
          <textarea v-model="form.description" rows="3" placeholder="事件描述"></textarea>
        </div>
        <div class="field">
          <label>涉及角色</label>
          <div v-if="characters.length" class="checkbox-group">
            <label v-for="c in characters" :key="c.id">
              <input v-model="form.involved" type="checkbox" :value="c.id" />
              {{ c.name }}
            </label>
          </div>
          <span v-else class="form-hint">暂无角色，可先在「角色」Tab 添加</span>
        </div>
        <span class="form-hint">保存可能需要几秒（首次触发向量化）</span>
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
      title="删除事件"
      :message="deleting ? `确认删除事件「${deleting.title}」？` : ''"
      :loading="deletingLoading"
      @confirm="doDelete"
      @cancel="deleting = null"
    />
  </div>
</template>
