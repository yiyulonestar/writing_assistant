<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{ stage: string }>()

const STEPS = [
  { key: 'planning', label: '规划大纲' },
  { key: 'retrieving', label: '检索设定' },
  { key: 'generating', label: '生成正文' },
  { key: 'reviewing', label: '一致性审稿' },
  { key: 'revising', label: '修正冲突' },
  { key: 'persisting', label: '保存章节' },
  { key: 'summarizing', label: '生成摘要' },
  { key: 'done', label: '完成' },
]

const activeIndex = computed(() => {
  if (props.stage === 'complete') return STEPS.length - 1
  const i = STEPS.findIndex((s) => s.key === props.stage)
  return i === -1 ? 0 : i
})
</script>

<template>
  <div class="progress-steps">
    <div
      v-for="(s, i) in STEPS"
      :key="s.key"
      class="progress-step"
      :class="{
        'progress-step--done': i < activeIndex,
        'progress-step--active': i === activeIndex,
      }"
    >
      <span class="progress-step__dot">{{ i < activeIndex ? '✓' : i + 1 }}</span>
      <span class="progress-step__label">{{ s.label }}</span>
    </div>
  </div>
</template>
