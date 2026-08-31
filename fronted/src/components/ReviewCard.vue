<script setup lang="ts">
import type { ReviewReport } from '../api/types'

defineProps<{ review?: ReviewReport | null }>()
</script>

<template>
  <div v-if="review" class="review-card">
    <div class="review-card__head">
      <span class="review-card__title">一致性审稿报告</span>
      <span v-if="review.conflicts.length === 0" class="badge badge--pass">已通过</span>
      <span v-else class="badge badge--conflict">存在未解决冲突</span>
    </div>

    <p v-if="review.summary" class="review-card__summary">{{ review.summary }}</p>

    <div v-if="review.conflicts.length" class="review-card__section">
      <div class="review-card__label review-card__label--danger">冲突（需人工介入）</div>
      <ul class="review-card__list">
        <li v-for="(c, i) in review.conflicts" :key="i">{{ c }}</li>
      </ul>
    </div>

    <div v-if="review.issues.length" class="review-card__section">
      <div class="review-card__label review-card__label--warn">问题</div>
      <ul class="review-card__list">
        <li v-for="(c, i) in review.issues" :key="i">{{ c }}</li>
      </ul>
    </div>
  </div>
</template>
