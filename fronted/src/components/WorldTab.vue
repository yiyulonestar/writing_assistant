<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { api } from '../api/client'
import type { WorldSetting } from '../api/types'
import { toast } from '../toast'
import Modal from './Modal.vue'
import ConfirmDialog from './ConfirmDialog.vue'

const props = defineProps<{ novelId: string }>()

const list = ref<WorldSetting[]>([])
const loading = ref(false)
const categoryFilter = ref('')

const categories = computed(() =>
  Array.from(new Set(list.value.map((w) => w.category).filter(Boolean))).sort(),
)
const filtered = computed(() =>
  categoryFilter.value ? list.value.filter((w) => w.category === categoryFilter.value) : list.value,
)

const showForm = ref(false)
const editing = ref<WorldSetting | null>(null)
const saving = ref(false)
const form = reactive({ category: '', name: '', description: '', parent_id: '', notes: '' })

// 父级下拉选项：排除当前正在编辑的项，避免自引用
const parentOptions = computed(() => list.value.filter((w) => w.id !== editing.value?.id))

const deleting = ref<WorldSetting | null>(null)
const deletingLoading = ref(false)

async function load() {
  loading.value = true
  try {
    list.value = await api.get<WorldSetting[]>(`/world-settings?novel_id=${props.novelId}`)
  } catch (e) {
    toast((e as Error).message, 'error')
  } finally {
    loading.value = false
  }
}

function openCreate() {
  editing.value = null
  form.category = ''
  form.name = ''
  form.description = ''
  form.parent_id = ''
  form.notes = ''
  showForm.value = true
}

function openEdit(w: WorldSetting) {
  editing.value = w
  form.category = w.category
  form.name = w.name
  form.description = w.description ?? ''
  form.parent_id = w.parent_id ?? ''
  form.notes = w.notes ?? ''
  showForm.value = true
}

function buildPayload() {
  return {
    category: form.category,
    name: form.name,
    description: form.description.trim() || null,
    parent_id: form.parent_id || null,
    notes: form.notes.trim() || null,
  }
}

async function submit() {
  if (!form.category.trim()) {
    toast('请填写设定分类', 'error')
    return
  }
  if (!form.name.trim()) {
    toast('请填写设定名称', 'error')
    return
  }
  saving.value = true
  try {
    if (editing.value) {
      await api.patch(`/world-settings/${editing.value.id}`, buildPayload())
      toast('已更新', 'success')
    } else {
      await api.post('/world-settings', { novel_id: props.novelId, ...buildPayload() })
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

function requestDelete(w: WorldSetting) {
  deleting.value = w
}

async function doDelete() {
  if (!deleting.value) return
  deletingLoading.value = true
  try {
    await api.del(`/world-settings/${deleting.value.id}`)
    toast('已删除', 'success')
    deleting.value = null
    await load()
  } catch (e) {
    toast((e as Error).message, 'error')
  } finally {
    deletingLoading.value = false
  }
}

function parentName(id?: string | null): string {
  if (!id) return ''
  return list.value.find((w) => w.id === id)?.name ?? ''
}

onMounted(load)
</script>

<template>
  <div>
    <div class="toolbar">
      <div style="display: flex; align-items: center; gap: 12px">
        <span class="muted">共 {{ list.length }} 条</span>
        <select v-model="categoryFilter" class="filter-select">
          <option value="">全部分类</option>
          <option v-for="c in categories" :key="c" :value="c">{{ c }}</option>
        </select>
      </div>
      <button class="btn btn--primary" @click="openCreate">＋ 新建设定</button>
    </div>

    <div v-if="loading" class="empty">加载中…</div>
    <div v-else-if="filtered.length === 0" class="empty">
      <p>还没有世界观设定，点击「新建设定」添加。</p>
    </div>
    <div v-else class="list">
      <div v-for="w in filtered" :key="w.id" class="list-item">
        <div class="list-item__main">
          <div class="list-item__title">
            {{ w.name }}
            <span class="badge">{{ w.category }}</span>
          </div>
          <div v-if="w.parent_id" class="muted">父级：{{ parentName(w.parent_id) }}</div>
          <div v-if="w.description" class="muted line-clamp">{{ w.description }}</div>
        </div>
        <div class="list-item__actions">
          <button class="btn btn--ghost btn--sm" @click="openEdit(w)">编辑</button>
          <button class="btn btn--danger btn--sm" @click="requestDelete(w)">删除</button>
        </div>
      </div>
    </div>

    <Modal :open="showForm" :title="editing ? '编辑设定' : '新建设定'" @close="showForm = false">
      <div class="form">
        <div class="field">
          <label>分类 <span class="req">*</span></label>
          <input v-model="form.category" list="world-categories" placeholder="如：宗门 / 功法 / 地理" />
          <datalist id="world-categories">
            <option v-for="c in categories" :key="c" :value="c"></option>
          </datalist>
        </div>
        <div class="field">
          <label>名称 <span class="req">*</span></label>
          <input v-model="form.name" placeholder="设定名称" />
        </div>
        <div class="field">
          <label>描述</label>
          <textarea v-model="form.description" rows="3" placeholder="设定描述"></textarea>
        </div>
        <div class="field">
          <label>父级设定</label>
          <select v-model="form.parent_id">
            <option value="">无（顶级）</option>
            <option v-for="p in parentOptions" :key="p.id" :value="p.id">{{ p.category }} / {{ p.name }}</option>
          </select>
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
      title="删除设定"
      :message="deleting ? `确认删除设定「${deleting.name}」？` : ''"
      :loading="deletingLoading"
      @confirm="doDelete"
      @cancel="deleting = null"
    />
  </div>
</template>
