# Repcal

個人飲食 / 重訓紀錄專案。Discord bot 為主要輸入介面，後端用 FastAPI + Postgres，未來加 LIFF/PWA 前端。

## 目前進度（Phase 1）

- ✅ Backend 骨架：FastAPI + SQLModel + Alembic
- ✅ Adapter pattern（messaging platform 可抽換）
- ✅ Discord bot + 第一個 slash command `/weight`
- ✅ Phase 1 DB schema：`users` / `user_identities` / `user_profiles` / `body_metrics` / `nutrition_phases`
- ✅ CI（lint + type check + test）
- ⏳ Phase 2：飲食紀錄 + Gemini 解析
- ⏳ Phase 3：重訓紀錄
- ⏳ Frontend (PWA 圖表)
- ⏳ Fly.io 部署

## 架構

```
[Discord App] ──gateway── [Bot (discord.py)]
                              │
                              ├─→ MessagingAdapter (Protocol)
                              │     └─ DiscordAdapter (現在)
                              │     └─ LineAdapter (未來)
                              │
                              ├─→ Services (Identity / Body / ...)
                              │
                              └─→ Repository (SQLModel)
                                    │
                                    └─→ Postgres (Supabase)
```

業務邏輯（services）跟 messaging 層解耦，未來搬到 LINE / Telegram 只要新增一個 adapter，service 一行不用改。

## 本機 setup

### 1. 安裝工具

```bash
# Python 管理工具（推薦 uv）
brew install uv

# Node（之後做前端用，現在不必）
brew install fnm

# Docker（之後部署用，現在不必）
# 從 docker.com 下載 Docker Desktop
```

### 2. 安裝 Python 依賴

```bash
cd backend
uv sync
```

uv 會自動建立 `.venv`、裝好所有套件、鎖定版本到 `uv.lock`。

### 3. 設定 `.env`

```bash
cd backend
cp .env.example .env
# 編輯 .env 填入：
#   - DATABASE_URL（Supabase）
#   - DISCORD_BOT_TOKEN（Discord Developer Portal）
#   - DISCORD_GUILD_ID（你的 dev server ID）
```

> `.env` 必須放在 `backend/` 目錄下（與 `pyproject.toml` 同層），
> 因為 `alembic`、`pytest`、`python -m repcal.main` 都從 `backend/` 執行。

### 4. 跑 migration 建表

```bash
cd backend
uv run alembic upgrade head
```

這會在 Supabase 建出 Phase 1 五張表。

### 5. 啟動 bot

```bash
cd backend
uv run python -m repcal.main
```

Bot 連上 Discord 後，到你 server 私訊 bot：

```
/weight value:72.5
```

應該回覆 `✓ 已紀錄 72.5kg（2026-05-15）`。

## 開發流程

```bash
# 新功能開分支
git checkout -b feat/your-feature

# 寫完跑檢查
cd backend
uv run ruff check .          # lint
uv run ruff format .         # format
uv run mypy src              # type check
uv run pytest                # test

# commit & push & PR
git add -A
git commit -m "feat: ..."
git push -u origin feat/your-feature
# 開 PR、CI 跑綠、merge
```

## 專案結構

```
repcal/
├── backend/
│   ├── pyproject.toml
│   ├── alembic/                  # DB migration
│   ├── src/repcal/
│   │   ├── config.py             # 從 .env 載入設定
│   │   ├── db.py                 # SQLAlchemy engine / session
│   │   ├── models/               # SQLModel 表定義
│   │   ├── adapters/             # MessagingAdapter (Discord/LINE/...)
│   │   ├── services/             # 業務邏輯（不依賴 adapter）
│   │   ├── bot/                  # Discord bot + slash commands
│   │   └── main.py               # FastAPI + bot 同 process 啟動
│   └── tests/
└── .github/workflows/ci.yml      # GitHub Actions
```
