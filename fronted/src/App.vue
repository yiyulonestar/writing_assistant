<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { store, go, type ViewName } from './store'
import { api } from './api/client'
import ToastHost from './components/ToastHost.vue'
import NovelList from './views/NovelList.vue'
import SettingsView from './views/SettingsView.vue'
import ChapterList from './views/ChapterList.vue'
import GenerateView from './views/GenerateView.vue'

const online = ref<'online' | 'offline' | 'checking'>('checking')

const nav: { key: ViewName; label: string; icon: string }[] = [
  { key: 'novels', label: '小说列表', icon: '📚' },
  { key: 'settings', label: '设定工作台', icon: '🧩' },
  { key: 'chapters', label: '章节', icon: '📝' },
  { key: 'generate', label: '生成', icon: '✨' },
]

async function checkHealth() {
  online.value = 'checking'
  try {
    await api.get('/health')
    online.value = 'online'
  } catch {
    online.value = 'offline'
  }
}

onMounted(checkHealth)
</script>

<template>
  <div class="app">
    <aside class="sidebar">
      <div class="brand">✍️ 写作辅助</div>
      <nav class="nav">
        <button
          v-for="n in nav"
          :key="n.key"
          class="nav__item"
          :class="{ 'nav__item--active': store.currentView === n.key }"
          @click="go(n.key)"
        >
          <span class="nav__icon">{{ n.icon }}</span>{{ n.label }}
        </button>
      </nav>
      <div class="sidebar__foot">
        <span class="dot" :class="`dot--${online}`"></span>
        <span>{{ online === 'online' ? '服务在线' : online === 'offline' ? '服务离线' : '检测中…' }}</span>
      </div>
    </aside>

    <div class="main">
      <header class="topbar">
        <div class="topbar__title">{{ store.currentNovelTitle || '未选择小说' }}</div>
        <button v-if="online !== 'online'" class="btn btn--ghost btn--sm" @click="checkHealth">
          重新检测
        </button>
      </header>

      <main class="content">
        <NovelList v-if="store.currentView === 'novels'" />

        <template v-else-if="store.currentNovelId">
          <SettingsView
            v-if="store.currentView === 'settings'"
            :key="store.currentNovelId"
            :novel-id="store.currentNovelId"
          />
          <ChapterList
            v-else-if="store.currentView === 'chapters'"
            :key="store.currentNovelId"
            :novel-id="store.currentNovelId"
          />
          <GenerateView v-else :key="store.currentNovelId" :novel-id="store.currentNovelId" />
        </template>

        <div v-else class="empty-block">
          <p>👈 请先在「小说列表」中选择一本小说</p>
        </div>
      </main>
    </div>

    <ToastHost />
  </div>
</template>
