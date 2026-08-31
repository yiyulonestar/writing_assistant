<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { api } from '../api/client'
import type { Character } from '../api/types'
import { toast } from '../toast'
import Modal from './Modal.vue'
import ConfirmDialog from './ConfirmDialog.vue'

const props = defineProps<{ novelId: string }>()

const list = ref<Character[]>([])
const loading = ref(false)

const showForm = ref(false)
const editing = ref<Character | null>(null)
const saving = ref(false)
const form = reactive({
  name: '',
  aliases: '',
  role: '',
  personality: '',
  background: '',
  appearance: '',
  goals: '',
  relationships: '',
  notes: '',
})

const deleting = ref<Character | null>(null)
const deletingLoading = ref(false)

async function load() {
  loading.value = true
  try {
    list.value = await api.get<Character[]>(`/characters?novel_id=${props.novelId}`)
  } catch (e) {
    toast((e as Error).message, 'error')
  } finally {
    loading.value = false
  }
}

function resetForm() {
  form.name = ''
  form.aliases = ''
  form.role = ''
  form.personality = ''
  form.background = ''
  form.appearance = ''
  form.goals = ''
  form.relationships = ''
  form.notes = ''
}

function openCreate() {
  editing.value = null
  resetForm()
  showForm.value = true
}

function openEdit(c: Character) {
  editing.value = c
  form.name = c.name
  form.aliases = (c.aliases ?? []).join(', ')
  form.role = c.role ?? ''
  form.personality = c.personality ?? ''
  form.background = c.background ?? ''
  form.appearance = c.appearance ?? ''
  form.goals = c.goals ?? ''
  form.relationships = serializeRelationships(c.relationships)
  form.notes = c.notes ?? ''
  showForm.value = true
}

function buildPayload() {
  return {
    name: form.name,
    aliases: splitList(form.aliases),
    role: form.role.trim() || null,
    personality: form.personality.trim() || null,
    background: form.background.trim() || null,
    appearance: form.appearance.trim() || null,
    goals: form.goals.trim() || null,
    relationships: parseRelationships(form.relationships) || null,
    notes: form.notes.trim() || null,
  }
}

async function submit() {
  if (!form.name.trim()) {
    toast('请填写角色名称', 'error')
    return
  }
  saving.value = true
  try {
    if (editing.value) {
      await api.patch(`/characters/${editing.value.id}`, buildPayload())
      toast('已更新', 'success')
    } else {
      await api.post('/characters', { novel_id: props.novelId, ...buildPayload() })
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

function requestDelete(c: Character) {
  deleting.value = c
}

async function doDelete() {
  if (!deleting.value) return
  deletingLoading.value = true
  try {
    await api.del(`/characters/${deleting.value.id}`)
    toast('已删除', 'success')
    deleting.value = null
    await load()
  } catch (e) {
    toast((e as Error).message, 'error')
  } finally {
    deletingLoading.value = false
  }
}

// 别名：逗号/顿号/分号分隔 → string[]
function splitList(text: string): string[] {
  return text
    .split(/[,，、;；]/)
    .map((s) => s.trim())
    .filter(Boolean)
}

// 人物关系：每行 "关系对象: 描述" → Record
function serializeRelationships(obj?: Record<string, string> | null): string {
  if (!obj) return ''
  return Object.entries(obj)
    .map(([k, v]) => `${k}: ${v}`)
    .join('\n')
}

function parseRelationships(text: string): Record<string, string> | undefined {
  const out: Record<string, string> = {}
  for (const raw of text.split('\n')) {
    const line = raw.trim()
    if (!line) continue
    const idx = line.search(/[:：]/)
    if (idx === -1) continue
    const k = line.slice(0, idx).trim()
    const v = line.slice(idx + 1).trim()
    if (k) out[k] = v
  }
  return Object.keys(out).length ? out : undefined
}

onMounted(load)
</script>

<template>
  <div>
    <div class="toolbar">
      <span class="muted">共 {{ list.length }} 个角色</span>
      <button class="btn btn--primary" @click="openCreate">＋ 新建角色</button>
    </div>

    <div v-if="loading" class="empty">加载中…</div>
    <div v-else-if="list.length === 0" class="empty">
      <p>还没有角色，点击「新建角色」添加。</p>
    </div>
    <div v-else class="list">
      <div v-for="c in list" :key="c.id" class="list-item">
        <div class="list-item__main">
          <div class="list-item__title">
            {{ c.name }}
            <span v-if="c.role" class="badge">{{ c.role }}</span>
          </div>
          <div v-if="c.aliases && c.aliases.length" class="muted">别名：{{ c.aliases.join('、') }}</div>
          <div v-if="c.personality" class="muted line-clamp">{{ c.personality }}</div>
        </div>
        <div class="list-item__actions">
          <button class="btn btn--ghost btn--sm" @click="openEdit(c)">编辑</button>
          <button class="btn btn--danger btn--sm" @click="requestDelete(c)">删除</button>
        </div>
      </div>
    </div>

    <Modal :open="showForm" :title="editing ? '编辑角色' : '新建角色'" @close="showForm = false">
      <div class="form">
        <div class="field">
          <label>名称 <span class="req">*</span></label>
          <input v-model="form.name" placeholder="角色名称" />
        </div>
        <div class="field">
          <label>别名</label>
          <input v-model="form.aliases" placeholder="用逗号分隔，如：三哥、小凡" />
        </div>
        <div class="field">
          <label>定位</label>
          <input v-model="form.role" placeholder="如：主角 / 反派 / 导师" />
        </div>
        <div class="field">
          <label>性格</label>
          <textarea v-model="form.personality" rows="2" placeholder="性格描述"></textarea>
        </div>
        <div class="field">
          <label>背景</label>
          <textarea v-model="form.background" rows="3" placeholder="背景故事"></textarea>
        </div>
        <div class="field">
          <label>外貌</label>
          <textarea v-model="form.appearance" rows="2" placeholder="外貌描述"></textarea>
        </div>
        <div class="field">
          <label>目标动机</label>
          <textarea v-model="form.goals" rows="2" placeholder="目标与动机"></textarea>
        </div>
        <div class="field">
          <label>人物关系</label>
          <textarea
            v-model="form.relationships"
            rows="3"
            placeholder="每行一条：对象: 关系描述（如：李四: 同门师兄）"
          ></textarea>
          <span class="form-hint">每行一条「对象: 描述」，留空表示无</span>
        </div>
        <div class="field">
          <label>备注</label>
          <textarea v-model="form.notes" rows="2" placeholder="备注"></textarea>
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
      title="删除角色"
      :message="deleting ? `确认删除角色「${deleting.name}」？` : ''"
      :loading="deletingLoading"
      @confirm="doDelete"
      @cancel="deleting = null"
    />
  </div>
</template>
