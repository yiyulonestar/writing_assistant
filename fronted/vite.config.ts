import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// 方案 B：Vite 代理，前端用相对路径，代码里不写死后端主机名。
// 后端已放行 5173 跨域，若想直连可去掉 proxy 并把 client.ts 的 BASE 改为 http://localhost:8000/api/v1。
export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        ws: true, // 生成进度 WebSocket 也走 /api/v1/generate/ws
      },
    },
  },
})
