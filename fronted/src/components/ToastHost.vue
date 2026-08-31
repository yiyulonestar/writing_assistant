<script setup lang="ts">
import { toasts, dismiss } from '../toast'
</script>

<template>
  <Teleport to="body">
    <div class="toasts">
      <TransitionGroup name="toast">
        <div
          v-for="t in toasts"
          :key="t.id"
          class="toast"
          :class="`toast--${t.type}`"
          @click="dismiss(t.id)"
        >
          <span>{{ t.message }}</span>
        </div>
      </TransitionGroup>
    </div>
  </Teleport>
</template>
