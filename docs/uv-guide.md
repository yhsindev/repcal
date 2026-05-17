# uv 指南

> Python 的套件管理 / 環境管理 / 版本管理工具。這份是 Repcal 專案實際用得到的部分，重點在「為什麼」跟「踩坑時怎麼處理」，不是把官方文件翻譯一遍。

## 目錄

1. [是什麼，為什麼](#1-是什麼為什麼)
2. [核心概念地圖](#2-核心概念地圖)
3. [常用指令速查](#3-常用指令速查)
4. [典型工作流程](#4-典型工作流程)
5. [跟其他工具比較](#5-跟其他工具比較)
6. [Trade-offs 與何時不用](#6-trade-offs-與何時不用)
7. [Troubleshooting](#7-troubleshooting)
8. [延伸閱讀](#8-延伸閱讀)

---

## 1. 是什麼，為什麼

### 一句話

`uv` 是 [Astral](https://astral.sh)（也是 ruff 作者）用 Rust 寫的 Python 工具鏈，**一次取代 pip / pip-tools / virtualenv / pyenv / pipx / poetry / pdm**。

### 為什麼這專案選它

| 痛點 | uv 怎麼解 |
|---|---|
| pip 慢（裝 100 個套件 1 分鐘） | 3 秒（10–20× 快） |
| `requirements.txt` 沒鎖 transitive deps，導致「在我電腦跑得起來」 | `uv.lock` 鎖死整棵依賴樹 + hash |
| Python 版本要靠 pyenv / homebrew / Anaconda 多套並存 | `uv python install 3.12` 一條指令 |
| 工具鏈太分散：venv、pip、pip-tools、pip-compile、pipx、pyenv... | 一個 `uv` 全包 |
| Poetry 速度慢、有些依賴解析 bug | uv 又快又嚴格 |

### 業界趨勢

2024 中以後 uv 採用率快速超越 Poetry。**新個人專案幾乎沒有不選 uv 的理由**。職缺、開源專案、文件範例越來越多用 uv，學了不會白學。

---

## 2. 核心概念地圖

理解 uv，只要把這四件東西的關係搞清楚就好：

```
┌────────────────────────┐
│  pyproject.toml        │  ← 你寫的：「我想要什麼」
│  - 專案 metadata       │
│  - dependencies        │
│  - dev-dependencies    │
└──────────┬─────────────┘
           │  uv add / uv remove / uv sync
           ↓
┌────────────────────────┐
│  uv.lock               │  ← uv 自動產生：「實際鎖死的版本」
│  - 完整依賴樹           │
│  - 每個套件的 hash      │
│  - 跨平台 markers       │
└──────────┬─────────────┘
           │  uv sync
           ↓
┌────────────────────────┐
│  .venv/                │  ← uv 自動建：「實際裝在哪」
│  虛擬環境，包含所有套件   │
└────────────────────────┘
```

| 檔案 / 資料夾 | 該不該 commit | 角色 |
|---|---|---|
| `pyproject.toml` | ✅ commit | 宣告檔，**你手動編輯**或 `uv add` 改 |
| `uv.lock` | ✅ commit | 自動產生，但**必須 commit** 才能 reproducible |
| `.venv/` | ❌ gitignore | 實際的 Python 環境，可隨時 `uv sync` 重建 |
| `.python-version` | 可選 commit | 指定 Python 版本（如 `3.12`） |

### 為什麼 `.venv/` 不 commit

裡面有平台特定的 binary（macOS arm64 vs Linux x86_64 不同），而且體積大（幾十 MB），重建只要幾秒。**lockfile 才是 reproducibility 的來源，不是 .venv**。

---

## 3. 常用指令速查

### 環境管理

| 指令 | 做什麼 | 何時用 |
|---|---|---|
| `uv sync` | 依 lockfile 把 `.venv` 同步到正確狀態 | clone 專案後、`pyproject.toml` 改過後 |
| `uv sync --frozen` | 同上，但**禁止更新** lockfile | CI 上、確保不會自己偷偷升 |
| `uv sync --no-dev` | 只裝 main 依賴，不裝 dev 工具 | 生產環境 Docker image |

### 依賴管理

| 指令 | 做什麼 |
|---|---|
| `uv add httpx` | 加套件到主依賴 + 更新 lockfile + 裝進 .venv |
| `uv add --dev pytest-mock` | 加到 dev group（測試 / lint / 開發用） |
| `uv add "httpx>=0.27,<0.30"` | 加套件並指定版本範圍 |
| `uv remove httpx` | 移除套件 + 更新 lockfile |
| `uv lock` | 重新解析 + 寫 lockfile（不裝） |
| `uv lock --upgrade` | 全部套件升到允許範圍內最新 |
| `uv lock --upgrade-package fastapi` | 只升 fastapi |

### 執行

| 指令 | 做什麼 |
|---|---|
| `uv run python script.py` | 用 .venv 裡的 Python 跑（**不用先 activate**） |
| `uv run pytest` | 用 .venv 裡的 pytest 跑 |
| `uv run python -m repcal.main` | 用 module 形式跑 |
| `uv run alembic upgrade head` | 跑安裝在 .venv 裡的 CLI 工具 |

**重點：在 uv 專案裡，你幾乎不需要 `source .venv/bin/activate`**。所有指令都 `uv run ...` 開頭，uv 會自動接管 venv。

### Python 版本管理

| 指令 | 做什麼 |
|---|---|
| `uv python list` | 列出所有可用 / 已裝的 Python 版本 |
| `uv python install 3.13` | 裝一個 Python 3.13 |
| `uv python install 3.11 3.12 3.13` | 一次裝多個 |
| `uv python pin 3.12` | 在當前目錄寫 `.python-version` 鎖住 |

### 全域 CLI 工具

uv 也能裝「跟專案無關」的 CLI 工具，類似 `pipx`：

| 指令 | 做什麼 |
|---|---|
| `uv tool install ruff` | 全域裝 ruff（不會污染專案 .venv） |
| `uv tool install httpie` | 裝 httpie 命令列工具 |
| `uvx ruff check .` | 一次性執行（不安裝） |

實際上你**不需要全域裝 ruff / mypy / pytest**，因為它們已經在這個專案的 dev dependencies 裡。但 `httpie`、`yt-dlp` 這種跟專案無關的工具放 `uv tool install` 比較乾淨。

---

## 4. 典型工作流程

### A. clone 別人專案來開發

```bash
git clone <url> && cd <repo>
uv sync                    # 一次搞定：裝 Python、建 venv、裝套件
uv run pytest              # 跑測試
```

不用 `python -m venv`、不用 `pip install -r requirements.txt`、不用 activate。

### B. 開新專案

```bash
uv init my-project         # 產生 pyproject.toml + README + 範例
cd my-project
uv add fastapi sqlmodel    # 加幾個依賴
uv run python -m my_project
```

### C. 加新套件

```bash
# 主依賴（生產也要）
uv add structlog

# 只在開發 / 測試用
uv add --dev pytest-asyncio

# 看改了什麼
git diff pyproject.toml uv.lock
```

注意：**永遠用 `uv add`，不要用 `pip install`**。`pip install` 不會更新 `pyproject.toml` 跟 `uv.lock`，下次 `uv sync` 會把它砍掉。

### D. 升級套件

```bash
# 看現在裝了什麼版本
uv pip list

# 升級單一套件到允許範圍內最新
uv lock --upgrade-package fastapi
uv sync

# 升級全部
uv lock --upgrade
uv sync

# 越過 pyproject.toml 範圍升大版（要先改 pyproject.toml）
# 例如把 "fastapi>=0.115" 改成 "fastapi>=0.120"
uv lock --upgrade-package fastapi
```

### E. 在 CI 上用

```yaml
# .github/workflows/ci.yml
- uses: astral-sh/setup-uv@v3
- run: uv python install 3.12
- run: uv sync --frozen           # 重點：--frozen 不允許更動 lockfile
- run: uv run pytest
```

`--frozen` 是 CI 上的鐵則：如果有人改了 `pyproject.toml` 但忘記 commit `uv.lock`，CI 會 fail，這正是你要的行為。

### F. 放進 Dockerfile

```dockerfile
FROM python:3.12-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev      # 只裝生產依賴

COPY . .
CMD ["uv", "run", "python", "-m", "repcal.main"]
```

---

## 5. 跟其他工具比較

### vs pip + venv

| | pip + venv | uv |
|---|---|---|
| 速度 | 慢 | 10–100× 快 |
| Lockfile | ❌（需要 pip-tools） | ✅ 內建 `uv.lock` |
| Python 版本管理 | ❌（要配 pyenv） | ✅ 內建 |
| 自動接 venv | ❌（要 activate） | ✅ `uv run` |
| 學習曲線 | 低 | 低 |

### vs Poetry

| | Poetry | uv |
|---|---|---|
| 速度 | 中（PubGrub 解析慢） | 快 |
| Lockfile | `poetry.lock` | `uv.lock` |
| 編譯來源 | Python | Rust |
| 依賴解析嚴格度 | 寬鬆 | 嚴格（採 PEP 標準） |
| 普及度（2024 起） | 緩慢下降 | 快速上升 |

實務上 uv 取代 Poetry 是 2024–2025 主流走向。如果你看到 Poetry 專案，知道概念類似就好。

### vs Conda / Mamba

完全不同流派。Conda 強項是**非 Python 的二進位依賴**（CUDA、編譯器、HDF5、ffmpeg 等），主要場景是科學運算 / ML / 資料工程。

- 純 Python 應用（FastAPI、Discord bot、爬蟲）→ **用 uv**
- 重 ML（PyTorch + CUDA + ffmpeg）→ Conda 還是有它的位置
- 兩者也能搭配：Conda 管系統依賴，uv 管 Python 套件

你這個專案是純 Python，uv 完勝。

### vs pipenv

pipenv 大概 2017–2018 紅過，現在基本被遺棄。看到 `Pipfile` 知道是這玩意就好，新專案別碰。

---

## 6. Trade-offs 與何時不用

uv 不是萬靈丹。誠實列一下：

### 何時 uv 沒那麼香

1. **舊 requirements.txt 專案改造**：可以做（`uv add -r requirements.txt`），但有時候會卡到奇怪的依賴衝突，要花點時間清
2. **超偏門 PyPI 套件**：少數套件 metadata 寫錯，pip 會容忍、uv 會嚴格拒絕。但這是套件的鍋，不是 uv 的鍋
3. **公司強制 Poetry**：團隊規範要遵守，個人也只能配合
4. **教學情境**：學 Python 第一週的人，pip + venv 還是比較好教（uv 概念多）

### 你已經養成的習慣中，要改掉的

```bash
# ❌ 不要這樣
pip install requests
python -m venv .venv
source .venv/bin/activate
python script.py
pip freeze > requirements.txt

# ✅ 改成這樣
uv add requests
uv run python script.py
# (.venv 跟 lockfile 自動處理)
```

---

## 7. Troubleshooting

### `uv: command not found`

uv 沒裝或不在 PATH：

```bash
brew install uv                    # macOS 推薦
# 或
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### `error: No virtual environment found`

```bash
uv sync     # 第一次跑會自動建 .venv 並裝套件
```

### `uv sync` 報 hash mismatch / lockfile 過期

通常是有人改了 `pyproject.toml` 但沒重新 lock：

```bash
uv lock        # 重新生 lockfile
uv sync        # 再同步
git add uv.lock
git commit -m "chore: update lockfile"
```

### CI 上 `uv sync --frozen` 失敗

```
error: Failed to update lockfile while frozen
```

意思是 lockfile 跟 pyproject.toml 不同步。本機修：

```bash
uv lock
git add uv.lock
git commit
```

### 我裝完套件，但 `import xxx` 還是找不到

確認你是用 `uv run python ...`，**不是直接 `python ...`**。直接 `python` 會用系統的 Python，不是 .venv 的。

或者你之前不小心 activate 別的 venv 還沒退出：

```bash
deactivate    # 退出舊 venv
uv run python -c "import xxx"
```

### Anaconda 的 `(base)` 跟 uv 衝突嗎？

不衝突。但你的 prompt 永遠顯示 `(base)` 會讓人誤以為在用 Anaconda 環境。其實只要你跑 `uv run ...`，uv 會強制用 .venv，base 環境只是個 prompt 標籤。

想完全隔離可以 `conda deactivate` 一次，把 base auto-activate 關掉：

```bash
conda config --set auto_activate_base false
```

### `discord_guild_id` parse error（這個我們踩過）

`.env` 寫 `DISCORD_GUILD_ID=`（空字串）會被 pydantic-settings parse 失敗。已在 `config.py` 加 validator 解掉，跟 uv 無關，記錄一下。

---

## 8. 延伸閱讀

- 官方文件：<https://docs.astral.sh/uv/>
- Astral blog（uv release notes）：<https://astral.sh/blog>
- PEP 621（pyproject.toml 標準）：<https://peps.python.org/pep-0621/>
- 與 pip / poetry 對比的中文整理：搜尋「uv pip 比較」

---

## 附錄：這專案實際用到的部分

開發迴圈 95% 時間只會用到這幾個指令：

```bash
# 第一次 setup
brew install uv
cd backend && uv sync

# 日常開發
uv run pytest                                # 跑測試
uv run ruff check .                          # lint
uv run ruff format .                         # format
uv run mypy src                              # type check
uv run alembic upgrade head                  # 跑 migration
uv run alembic revision -m "..." --autogenerate    # 產新 migration
uv run python -m repcal.main                 # 啟動 bot

# 改依賴
uv add <package>
uv add --dev <package>
git add pyproject.toml uv.lock
git commit
```

其他指令偶爾用到，回來這份文件查就好。
