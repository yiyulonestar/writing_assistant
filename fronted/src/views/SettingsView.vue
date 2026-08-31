<script setup lang="ts">
import { ref } from 'vue'
import CharacterTab from '../components/CharacterTab.vue'
import WorldTab from '../components/WorldTab.vue'
import TimelineTab from '../components/TimelineTab.vue'

defineProps<{ novelId: string }>()

const tab = ref<'character' | 'world' | 'timeline'>('character')

const tabs = [
  { key: 'character', label: '角色' },
  { key: 'world', label: '世界观' },
  { key: 'timeline', label: '时间线' },
] as const
</script>

<template>
  <div class="view">
    <div class="tabs">
      <button
        v-for="t in tabs"
        :key="t.key"
        class="tab"
        :class="{ 'tab--active': tab === t.key }"
        @click="tab = t.key"
      >
        {{ t.label }}
      </button>
    </div>

    <CharacterTab v-if="tab === 'character'" :novel-id="novelId" />
    <WorldTab v-else-if="tab === 'world'" :novel-id="novelId" />
    <TimelineTab v-else :novel-id="novelId" />
  </div>
</template>
