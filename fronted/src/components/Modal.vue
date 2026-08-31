<script setup lang="ts">
defineProps<{ open: boolean; title?: string; width?: string }>()
defineEmits<{ close: [] }>()
</script>

<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="open" class="modal-backdrop" @click.self="$emit('close')">
        <div class="modal" :style="{ width: width || '560px' }">
          <header class="modal__head">
            <h3>{{ title }}</h3>
            <button class="modal__close" @click="$emit('close')">×</button>
          </header>
          <div class="modal__body"><slot /></div>
          <footer v-if="$slots.footer" class="modal__foot"><slot name="footer" /></footer>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>
