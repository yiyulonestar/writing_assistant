import { reactive } from 'vue'

export interface Toast {
  id: number
  message: string
  type: 'info' | 'success' | 'error'
}

let seq = 0
export const toasts = reactive<Toast[]>([])

export function dismiss(id: number) {
  const i = toasts.findIndex((t) => t.id === id)
  if (i >= 0) toasts.splice(i, 1)
}

export function toast(message: string, type: Toast['type'] = 'info') {
  const id = ++seq
  toasts.push({ id, message, type })
  setTimeout(() => dismiss(id), 4000)
}
