# Git 与 GitHub 使用指南

> 一份**通用**的 Git + GitHub 上传 / 协作指南，不限于本项目；用本项目（`writing_assistant`，后端 FastAPI + 前端 Vue3）作为贯穿示例。命令以 Windows（Git Bash / PowerShell）为主，macOS / Linux 仅路径写法略有差异，命令通用。

---

## 目录

1. [Git 与 GitHub 是什么](#1-git-与-github-是什么)
2. [安装与环境准备](#2-安装与环境准备)
3. [核心概念速览](#3-核心概念速览)
4. [第一次：初始化本地仓库](#4-第一次初始化本地仓库)
5. [.gitignore：别把不该传的传上去](#5-gitignore别把不该传的传上去)
6. [日常工作流：改代码 → 提交 → 推送](#6-日常工作流改代码--提交--推送)
7. [关联 GitHub 并推送](#7-关联-github-并推送)
8. [分支与协作](#8-分支与协作)
9. [常用命令速查表](#9-常用命令速查表)
10. [用本项目完整走一遍](#10-用本项目完整走一遍)
11. [常见问题排查](#11-常见问题排查)
12. [好习惯清单](#12-好习惯清单)

---

## 1. Git 与 GitHub 是什么

| 概念 | 说明 |
|------|------|
| **Git** | 一个**分布式版本控制工具**，跑在本地，记录文件的每次改动历史，支持分支、回滚、合并。不联网也能用。 |
| **GitHub** | 一个**托管 Git 仓库的网站**（类似还有 GitLab、Gitee），把本地仓库同步到云端，方便备份、多人协作、代码评审。 |
| **本地仓库 / 远程仓库** | 本地仓库在你电脑上；远程仓库在 GitHub 上。二者通过 `push`（上传）/ `pull`（下载）同步。 |

一句话：**Git 管版本，GitHub 管托管**。本指南覆盖「把本地项目上传到 GitHub」以及日常「改完代码提交推送」的完整流程。

---

## 2. 安装与环境准备

### 2.1 安装 Git

- **Windows**：到 <https://git-scm.com/download/win> 下载安装（安装时一路默认即可，会附带 Git Bash）。
- **macOS**：`brew install git`，或 `xcode-select --install`。
- **Linux**：`sudo apt install git`（Debian/Ubuntu）/ `sudo yum install git`（CentOS）。

验证：

```bash
git --version
# git version 2.54.0.windows.1
```

### 2.2 配置身份（每台机器一次）

提交记录会附带姓名和邮箱，需先配置（**全局**配置一次即可，对所有仓库生效）：

```bash
git config --global user.name  "你的名字"
git config --global user.email "you@example.com"   # 建议用 GitHub 注册邮箱
```

查看是否生效：

```bash
git config --global --list
```

> 只想对**当前项目**单独配置（不全局），把 `--global` 去掉再执行即可。

### 2.3 认证方式：HTTPS Token 还是 SSH Key

把代码推到 GitHub 需要身份认证，二选一即可（**新手推荐 HTTPS + Token**）：

| 方式 | 优点 | 缺点 |
|------|------|------|
| **HTTPS + Personal Access Token** | 配置简单，无需生成密钥对 | 每次推送可能要求填 token（可配置缓存） |
| **SSH Key** | 配置一次永久免密，体验最好 | 首次配置稍多几步 |

#### 方式 A：HTTPS + Token（推荐新手）

1. GitHub → 右上角头像 → **Settings** → **Developer settings** → **Personal access tokens** → **Tokens (classic)** → **Generate new token**。
2. 勾选 `repo`（读写仓库）权限，生成后**复制保存**（只显示一次）。
3. 推送时用户名填 GitHub 用户名，**密码处粘贴 token**（不是登录密码）。

> 2021 年起 GitHub 不再支持用账号密码走 HTTPS，必须用 Token。

#### 方式 B：SSH Key（一劳永逸）

```bash
ssh-keygen -t ed25519 -C "you@example.com"   # 一路回车，默认路径即可
cat ~/.ssh/id_ed25519.pub                     # 复制输出内容
```

把公钥内容粘贴到 GitHub → **Settings** → **SSH and GPG keys** → **New SSH key**。之后远程地址用 `git@github.com:用户名/仓库名.git` 形式。

验证：

```bash
ssh -T git@github.com    # 首次会提示确认，输入 yes；出现 "Hi 用户名!" 即成功
```

---

## 3. 核心概念速览

| 概念 | 类比 | 说明 |
|------|------|------|
| **工作区（Working Directory）** | 你正在编辑的文件夹 | 文件的实际内容 |
| **暂存区（Staging / Index）** | 购物车 | `git add` 后，决定哪些改动要提交 |
| **本地仓库（Repository）** | 已结账的账本 | `git commit` 后，改动被正式记录 |
| **远程仓库（Remote）** | 云端账本 | GitHub 上的仓库，`origin` 是其默认别名 |
| **提交（Commit）** | 一次快照 | 一个不可变的历史节点，有唯一哈希（如 `a1b2c3d`） |
| **分支（Branch）** | 平行世界 | 主分支 `main`，可另开分支开发新功能再合并 |
| **HEAD** | 当前指针 | 指向「你现在所在」的分支 / 提交 |

数据流：**工作区 →(add)→ 暂存区 →(commit)→ 本地仓库 →(push)→ 远程仓库**

---

## 4. 第一次：初始化本地仓库

两种起点，选其一：

### 4.1 从零开始（已有本地项目，本项目就是这种情况）

```bash
cd /path/to/your-project      # 例如本项目：cd F:/code/writing_assistant
git init                      # 在当前目录创建 .git，成为 Git 仓库
```

### 4.2 从 GitHub 克隆已有仓库

```bash
git clone https://github.com/用户名/仓库名.git
# 或 SSH：
git clone git@github.com:用户名/仓库名.git
cd 仓库名
```

---

## 5. .gitignore：别把不该传的传上去

**这一步至关重要**，尤其当你项目里有密钥、依赖目录、构建产物时。`.gitignore` 文件里列出的路径会被 Git 自动忽略，不进入版本控制。

### 5.1 本项目为什么必须配置

本项目（`writing_assistant`）存在这些**不该上传**的内容：

| 路径 | 类型 | 为什么不能传 |
|------|------|--------------|
| `backend/.env` | **敏感信息** | 里面含 `DASHSCOPE_API_KEY` 等密钥，一旦上传等于公开 |
| `backend/__pycache__/`、`*.pyc` | 缓存 | 自动生成，无用 |
| `backend/.venv/`、`venv/` | 虚拟环境 | 体积大，应各自本地重建 |
| `fronted/node_modules/` | 依赖 | 体积巨大，`package.json` 已记录依赖，可 `npm install` 重建 |
| `fronted/dist/` | 构建产物 | 可重新 `npm run build` 生成 |
| `.idea/`、`.vscode/` | 编辑器配置 | 个人偏好，非项目代码 |
| `.DS_Store`、`Thumbs.db` | 系统文件 | 无用 |

### 5.2 推荐：在项目根目录放一份统一 .gitignore

本项目 `backend/.gitignore` 已存在，但根目录没有。**建议在根目录创建一份**，覆盖前后端所有该忽略的内容：

```gitignore
# ---- Python（后端）----
__pycache__/
*.py[cod]
*.egg-info/
.venv/
venv/
.pytest_cache/
.ruff_cache/
*.sqlite3

# ---- Node（前端）----
node_modules/
dist/
*.local
npm-debug.log*
yarn-error.log*
pnpm-debug.log*

# ---- 环境变量 / 敏感信息 ----
.env
.env.*
!.env.example          # 保留示例文件（不含真实密钥）

# ---- 编辑器 / 系统 ----
.idea/
.vscode/
.DS_Store
Thumbs.db

# ---- 本地工具状态（可选，按需保留）----
.claude/settings.local.json
```

> 说明：`backend/.gitignore` 和根 `.gitignore` 可以并存（子目录规则同样生效）。若想统一管理，把根目录这份保留、`backend/.gitignore` 可删可留。

### 5.3 敏感信息三原则

1. **密钥只放 `.env`，`.env` 必须进 `.gitignore`**；同时提供一份 `backend/.env.example`（占位符示例，不含真实值）供他人参考。
2. **检查是否已把敏感文件误加**：提交前 `git status` 确认 `.env` 不在待提交列表里。
3. **若密钥曾上传到 GitHub**：**立即去服务商后台重置（轮换）该密钥**，而不是只删文件——因为 GitHub 的提交历史里还留着旧值，删了也没用。

> 本项目 `backend/.env` 里确实有真实的 `DASHSCOPE_API_KEY`，上传前务必确认它被忽略；若历史上传过，请去 DashScope 控制台重置该 key。

---

## 6. 日常工作流：改代码 → 提交 → 推送

每次改完一批代码，走这条固定流程：

```bash
git status                  # 1. 看改了什么、哪些是新增/修改/删除
git add .                   # 2. 全部加入暂存区（或 git add 具体文件）
git status                  # 3. 再确认暂存区内容是否符合预期
git commit -m "feat: 新增章节生成面板"   # 4. 提交到本地仓库
git push                    # 5. 推送到 GitHub（首次可能需 git push -u origin main）
```

- `git add .` 加所有改动；`git add src/App.vue` 只加指定文件；`git add -A` 含删除。
- 提交前用 `git diff` 看具体改动，`git diff --staged` 看暂存区的改动。

### 6.1 提交信息规范（Conventional Commits）

推荐这种格式，可读性高、方便自动生成版本号 / changelog：

```
<类型>(<范围>): <简述>
```

| 类型 | 含义 | 示例 |
|------|------|------|
| `feat` | 新功能 | `feat: 新增小说管理 CRUD` |
| `fix` | 修复 bug | `fix: 修复删除小说未刷新列表` |
| `docs` | 文档 | `docs: 补充部署说明` |
| `chore` | 杂项/构建/依赖 | `chore: 初始化前端脚手架` |
| `refactor` | 重构（不改变行为） | `refactor: 抽出 api 客户端` |
| `style` | 样式/格式 | `style: 统一按钮间距` |
| `test` | 测试 | `test: 新增章节接口测试` |

### 6.2 回退误操作（高频）

```bash
git restore 文件名            # 丢弃工作区某文件的改动（回到上次提交状态）
git restore --staged 文件名    # 把文件从暂存区移回工作区（取消 add）
git reset --soft HEAD~1       # 撤销最近一次 commit，改动保留在暂存区
git reset --hard HEAD~1       # ⚠️ 撤销 commit 并丢弃改动（谨慎！不可恢复）
git revert <提交哈希>          # 用一次新提交来“抵消”某次历史提交（安全，推荐用于已推送的提交）
```

---

## 7. 关联 GitHub 并推送

### 7.1 在 GitHub 上建远程仓库

1. 登录 GitHub → 右上角 **+** → **New repository**。
2. 填 **Repository name**（如 `writing_assistant`）。
3. 建议**不要勾选** “Add a README / .gitignore / license”（避免与本地的冲突）。
4. 选择 Public 或 Private → **Create repository**。

### 7.2 关联并第一次推送

创建仓库后页面会给出命令，核心就是：

```bash
git remote add origin https://github.com/你的用户名/writing_assistant.git
git branch -M main                    # 把本地分支重命名为 main（与 GitHub 默认一致）
git push -u origin main               # -u 建立跟踪关系，之后可省略 origin main 直接 git push
```

- `git remote -v` 查看当前远程地址；`git remote set-url origin <新地址>` 修改远程地址；`git remote remove origin` 删除远程。
- SSH 用户把地址换成 `git@github.com:你的用户名/writing_assistant.git`。

### 7.3 用 gh CLI 一步到位（可选）

装了 GitHub 官方 CLI（`gh`）后更省事：

```bash
gh auth login              # 一次性登录授权
gh repo create writing_assistant --private --source=. --remote=origin --push
```

---

## 8. 分支与协作

单人项目通常直接在 `main` 上推进；多人协作或做较大改动时用分支：

```bash
git branch feature/xxx      # 创建新分支
git checkout feature/xxx    # 切换到该分支（或 git switch feature/xxx）
git checkout -b feature/xxx # 创建并切换（一步到位）

# 开发完成后，回到 main 合并：
git checkout main
git merge feature/xxx       # 把 feature/xxx 合并进 main
git branch -d feature/xxx   # 删除本地分支
```

多人协作常用 **Pull Request（PR）**：把功能分支 `push` 到 GitHub，在网页上发起 PR，让他人 review 后再合并进 `main`。

- `git pull` = `git fetch` + `git merge`：拉取远程并合并到当前分支。
- `git pull --rebase`：拉取后把你的提交“重放”到最新之上，历史更线性（个人分支常用）。

---

## 9. 常用命令速查表

| 命令 | 作用 |
|------|------|
| `git init` | 初始化本地仓库 |
| `git clone <url>` | 克隆远程仓库 |
| `git status` | 查看工作区/暂存区状态 |
| `git diff` / `git diff --staged` | 看改动 / 看暂存区改动 |
| `git add .` / `git add <file>` | 加入暂存区 |
| `git commit -m "msg"` | 提交 |
| `git log --oneline --graph` | 查看提交历史（图形化） |
| `git push` / `git push -u origin main` | 推送 |
| `git pull` | 拉取并合并远程 |
| `git fetch` | 只拉取远程，不合并 |
| `git branch` / `git branch -a` | 看本地 / 所有分支 |
| `git checkout <分支/文件>` | 切换分支 / 恢复文件 |
| `git merge <分支>` | 合并分支 |
| `git rebase <分支>` | 变基 |
| `git stash` / `git stash pop` | 暂存未提交改动 / 恢复 |
| `git restore <file>` | 丢弃工作区改动 |
| `git reset` / `git revert` | 回退（见 6.2） |
| `git remote -v` | 查看远程仓库地址 |
| `git tag v1.0.0` | 打标签（发版本） |
| `git rm --cached <file>` | 从版本控制移除但仍保留本地文件（用于补救误加文件） |

---

## 10. 用本项目完整走一遍

以本项目 `writing_assistant` 为例，从零到推上 GitHub 的完整命令：

```bash
# 0) 进入项目根目录
cd F:/code/writing_assistant

# 1) 初始化仓库
git init

# 2) 在根目录创建 .gitignore（内容见第 5 节；重点排除 .env / node_modules / dist / __pycache__）
#    确认 backend/.env 已被忽略：
git status
#    输出里【不应出现】 backend/.env 和 fronted/node_modules

# 3) 配置身份（若还没全局配过）
git config --global user.name  "你的名字"
git config --global user.email "you@example.com"

# 4) 首次提交
git add .
git status                      # 最后确认一遍暂存区没有敏感文件
git commit -m "chore: 初始化项目（后端 FastAPI + 前端 Vue3）"

# 5) 在 GitHub 网页上创建同名空仓库 writing_assistant（不要勾选 README/.gitignore）

# 6) 关联远程并推送
git remote add origin https://github.com/你的用户名/writing_assistant.git
git branch -M main
git push -u origin main

# 7) 之后每次改完代码，就是三步：
git add .
git commit -m "feat: 描述本次改动"
git push
```

### 10.1 本项目推荐的首次提交结构（举例）

| 应提交 ✅ | 应忽略 ❌ |
|-----------|-----------|
| `backend/app/**`（源码） | `backend/.env`（密钥） |
| `backend/pyproject.toml`、`README.md` | `backend/__pycache__/`、`.venv/` |
| `fronted/src/**`、`package.json`、`vite.config.ts` | `fronted/node_modules/`、`fronted/dist/` |
| `使用说明.md`、`开发文档.md`、`fronted/前端开发文档.md` | `.idea/`、`.vscode/` |

> 提示：`pyproject.toml` / `package.json` / `uv.lock` / `package-lock.json` 是**依赖清单，应提交**，他人据此重建环境；而 `node_modules`、`.venv`、`dist` 是**可重建产物，应忽略**。

---

## 11. 常见问题排查

| 报错 / 现象 | 原因 | 解决 |
|-------------|------|------|
| `fatal: not a git repository` | 当前目录不是仓库 | `cd` 到仓库根目录，或先 `git init` |
| `Authentication failed` | 用了账号密码而非 Token | 改用 Personal Access Token（见 2.3） |
| `Permission denied (publickey)` | SSH 公钥没配或没添加到 GitHub | 见 2.3 方式 B，`ssh -T git@github.com` 验证 |
| `remote: Repository not found` | 地址写错 / 无权限 / 仓库不存在 | 核对用户名与仓库名，`git remote -v` 检查 |
| `failed to push ... rejected` | 远程有新提交，本地落后 | 先 `git pull --rebase` 再 `git push` |
| `error: failed to push ... tip of your current branch` | 同上 | 同上 |
| `.env` 已经在待提交里 | `.gitignore` 没生效（文件此前已被跟踪） | `git rm --cached backend/.env` 移除跟踪，再确认 `.gitignore` 有 `.env` |
| 想彻底删掉已提交的密钥历史 | 普通删文件不够，历史里还有 | 优先**轮换密钥**；确需清除历史需 `git filter-repo`（高级操作） |

---

## 12. 好习惯清单

- [ ] 提交前先 `git status`，确认没有误加敏感文件（`.env`、密钥、大文件）。
- [ ] 每次提交只做一件事，提交信息写清楚（用 Conventional Commits）。
- [ ] 密钥一律进 `.env` + `.gitignore`，并提供 `.env.example`。
- [ ] 依赖清单（`package.json` / `pyproject.toml`）要提交，产物（`node_modules` / `dist` / `.venv`）要忽略。
- [ ] 推送前先 `git pull`（或 `--rebase`），避免冲突堆积。
- [ ] 定期 `git push`，把本地进度备份到 GitHub。
- [ ] 已推送到远程的提交，尽量用 `git revert` 而不是 `git reset --hard` 来“反悔”。
- [ ] 换电脑 / 新环境，用 `git clone` 拉下来，而不是复制文件夹。

---

## 附：本项目技术栈速查（配合示例理解）

| 目录 | 技术 | 构建产物 | 依赖清单 | 应忽略 |
|------|------|----------|----------|--------|
| `backend/` | Python + FastAPI | ——（无） | `pyproject.toml` + `uv.lock` | `__pycache__/`、`.venv/`、`.env` |
| `fronted/` | Vue 3 + Vite | `dist/` | `package.json` + `package-lock.json` | `node_modules/`、`dist/` |
