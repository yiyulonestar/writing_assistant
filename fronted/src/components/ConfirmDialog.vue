<script setup lang="ts">
import Modal from './Modal.vue'

withDefaults(
  defineProps<{
    open: boolean
    title?: string
    message?: string
    confirmText?: string
    loading?: boolean
  }>(),
  { title: '确认操作', message: '', confirmText: '确认删除', loading: false },
)

const emit = defineEmits<{ confirm: []; cancel: [] }>()
</script>

<template>
  <Modal :open="open" :title="title" width="440px" @close="emit('cancel')">
    <p class="confirm-msg">{{ message }}</p>
    <template #footer>
      <button class="btn" @click="emit('cancel')">取消</button>
      <button class="btn btn--danger" :disabled="loading" @click="emit('confirm')">
        {{ loading ? '处理中…' : confirmText }}
      </button>
    </template>
  </Modal>
</template>
