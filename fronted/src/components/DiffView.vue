<script setup lang="ts">
// unified diff 行着色：+ 新增 / - 删除 / @@ 区块 / --- +++ 文件头
defineProps<{ lines: string[] }>()

function lineClass(line: string): string {
  if (line.startsWith('+++') || line.startsWith('---')) return 'diff-line--header'
  if (line.startsWith('@@')) return 'diff-line--hunk'
  if (line.startsWith('+')) return 'diff-line--add'
  if (line.startsWith('-')) return 'diff-line--del'
  return 'diff-line--ctx'
}
</script>

<template>
  <div class="diff-view">
    <template v-if="lines.length">
      <div v-for="(l, i) in lines" :key="i" class="diff-line" :class="lineClass(l)">
        <span class="diff-line__sign">{{ l.charAt(0) }}</span>
        <span class="diff-line__text">{{ l.slice(1) }}</span>
      </div>
    </template>
    <div v-else class="muted">两版本内容相同，无差异。</div>
  </div>
</template>
