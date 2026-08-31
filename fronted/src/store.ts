import { reactive } from 'vue'

export type ViewName = 'novels' | 'settings' | 'chapters' | 'generate'

export const store = reactive({
  currentView: 'novels' as ViewName,
  currentNovelId: '',
  currentNovelTitle: '',
  currentChapterId: '',
})

export function go(view: ViewName) {
  store.currentView = view
}

export function selectNovel(id: string, title: string) {
  store.currentNovelId = id
  store.currentNovelTitle = title
  store.currentChapterId = ''
  store.currentView = 'settings'
}

export function openChapter(chapterId: string) {
  store.currentChapterId = chapterId
  store.currentView = 'chapters'
}
