# 写作辅助 · 前端

长篇小说 / 网文创作辅助 Agent 的 Web 前端，覆盖「设定 → 生成 → 审稿 → 重写」完整闭环。

- 后端：FastAPI + Tortoise ORM + PostgreSQL(pgvector)，接口基路径 `/api/v1`（见 `backend/` 与 `使用说明.md`）
- 前端：Vite + Vue 3（Composition API + `<script setup>`）+ TypeScript，刻意**不引入**路由、状态库、UI 框架、HTTP 库

## 技术栈（最小化）

| 层 | 选型 | 说明 |
|----|------|------|
| 构建 / 开发服务器 | Vite | dev server + 代理（顺带解决 CORS）+ 打包 |
| 框架 | Vue 3（`<script setup>`） | 响应式 + 单文件组件 |
| HTTP | 原生 `fetch` | 封装为 `src/api/client.ts` |
| 实时进度 | 原生 `WebSocket` | 封装为 `src/api/ws.ts` |
| 状态 | `reactive()`（单个 `store.ts`） | 全局选中小说 / 章节 / 视图 |
| 路由 | 无（响应式标志切换视图） | 5~6 个视图，不值当引 vue-router |
| 样式 | 纯 CSS（`src/styles/main.css`） | 统一设计 token，无 UI 框架 |

最终运行时依赖只有 `vue`；开发期依赖 `vite`、`@vitejs/plugin-vue`、`typescript`、`vue-tsc`。

## 目录结构

```
fronted/
├── index.html                 # 入口
├── package.json
├── vite.config.ts             # Vite + 代理配置
├── tsconfig.json
└── src/
    ├── main.ts                # createApp 挂载
    ├── App.vue                # 顶栏 + 侧边栏 + 视图切换 + 健康检查
    ├── env.d.ts
    ├── store.ts               # reactive 全局状态
    ├── toast.ts               # 全局 toast
    ├── api/
    │   ├── client.ts          # fetch 封装（baseURL、X-API-Key、JSON、错误）
    │   ├── types.ts           # 后端 schema → TS 类型（snake_case）
    │   └── ws.ts              # WebSocket 生成进度
    ├── components/
    │   ├── Modal.vue          # 通用弹窗
    │   ├── ConfirmDialog.vue  # 二次确认
    │   ├── ToastHost.vue      # toast 容器
    │   ├── DiffView.vue       # 草稿版本 diff 行着色
    │   ├── ProgressSteps.vue  # 生成进度步骤条
    │   ├── ReviewCard.vue     # 审稿报告卡片
    │   ├── CharacterTab.vue   # 角色 CRUD
    │   ├── WorldTab.vue       # 世界观 CRUD
    │   └── TimelineTab.vue    # 时间线 CRUD
    ├── views/
    │   ├── NovelList.vue      # 小说列表 + 新建/编辑/删除
    │   ├── SettingsView.vue   # 设定工作台（角色/世界观/时间线 三 Tab）
    │   ├── ChapterList.vue    # 章节列表
    │   ├── ChapterEditor.vue  # 正文编辑 + 草稿/diff + 局部重写
    │   └── GenerateView.vue   # 生成面板 + 进度 + 审稿报告
    └── styles/
        └── main.css
```

## 环境要求

- Node.js ≥ 18（已在 Node 22 验证）
- 后端已启动，默认 `http://localhost:8000`（见 `backend/README.md` 或 `使用说明.md`）

## 快速开始（开发）

```bash
cd fronted
npm install
npm run dev        # 打开 http://localhost:5173
```

开发期前端走 **Vite 代理**（`vite.config.ts` 把 `/api` 代理到 `http://localhost:8000`，含 `ws: true`），代码里 baseURL 用相对路径 `'/api/v1'`（见 `src/api/client.ts`），不写死后端主机名。

> 页面顶部会显示后端健康状态（`GET /health`）：绿点「服务在线」/ 红点「服务离线」。离线时点「重新检测」。

## 生产部署（同源，单端口）

```bash
cd fronted
npm run build      # vue-tsc 类型检查 + vite build → dist/
```

后端已在 `backend/app/main.py` 里加了 `StaticFiles` 挂载：**当 `fronted/dist` 存在时，后端在 `/` 直接托管前端产物**，`/api/v1/*` 与 `/docs` 不受影响。

```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000
# 访问 http://localhost:8000 即为完整应用（前端 + 接口同源，无跨域）
```

> 开发期若无 `dist` 目录，后端 `/` 仍返回 JSON 兜底，不影响 Vite dev server。

## 配置说明

| 项 | 位置 | 说明 |
|----|------|------|
| 后端基地址 | `src/api/client.ts` 的 `BASE` | 默认 `'/api/v1'`（走代理/同源）。直连后端改成 `'http://localhost:8000/api/v1'` |
| API Key | `src/api/client.ts` 的 `API_KEY` | 后端 `.env` 若配置 `API_KEY`，在此填写（带在 CRUD 上无害）；未配置则留空 |
| CORS | 后端 `.env` 的 `CORS_ORIGINS` | 默认已放行 5173；换端口/局域网访问需追加来源并重启后端 |

## 功能清单

- **小说管理**：列表 + 新建 / 编辑 / 删除（级联删除警示）+ 选中进入工作台
- **设定管理**：角色（别名多值、人物关系键值对）/ 世界观（`category` 过滤、`parent_id` 层级）/ 时间线（`order_index` 排序、`status` 枚举、涉及角色多选）三个 Tab 的 CRUD
- **章节写作**：章节列表 + 正文编辑（实时字数，按中文字符计）+ 大纲 / 摘要 / 状态 + 草稿版本历史 + 两版 diff 对比
- **生成流水线**：单章（HTTP 完整模式 / WebSocket 实时进度）+ 批量，实时进度条 + 审稿报告（issues / conflicts / summary / 是否已修复）
- **局部重写**：按空行分段选择段落范围 + 指令重写，成功后回填正文并自动留存新草稿版本

## 关键约定与注意事项

- **字段名 snake_case**：前端 JSON 直接用 `novel_id` / `word_count` / `involved_character_ids` 等，**勿转 camelCase**，否则后端校验丢字段。
- **`PATCH` 部分更新**：本前端用「完整可编辑字段 + 空值置 `null`」发送（`null` 会清空字段），因此编辑表单会把现有字段全部回填，避免误清已有数据。
- **`DELETE` 返回 204**：`client.ts` 先判断 204 再解析，避免 `res.json()` 抛错。
- **审稿报告只在 HTTP 生成响应里**：`POST /generate/chapter` 返回完整 `review`；`WS /generate/ws` 只回 `chapter_id` + `word_count`。所以单章生成「完整模式」能看审稿报告，「实时进度」模式需完成后按 `chapter_id` 回拉正文（无审稿报告）。
- **生成 / 重写较慢**（分钟级）：前端已做异步 + 进度 + 防重复提交 + loading 态；首次保存设定或生成时可能触发 embedding / LLM 冷启动，属正常。
- **UUID 全为字符串**：不要当 number 处理。
- **章节字数 = 中文字符数**：与后端 `services/stats.py` 的 `count_words` 一致。

## 常用脚本

| 命令 | 说明 |
|------|------|
| `npm run dev` | 启动 Vite 开发服务器（5173，代理到 8000） |
| `npm run build` | `vue-tsc --noEmit` 类型检查 + `vite build` 产出 `dist/` |
| `npm run preview` | 本地预览构建产物 |
| `npm run typecheck` | 仅类型检查 |
