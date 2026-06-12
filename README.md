# 智能体沙箱武器库 (Agent Sandbox Arsenal) V2.0

本项是一个极简、非侵入式、跨 IDE 自适应的本地 AI 辅助开发侧车套件。支持免配置海外抓取与 D 盘环境隔离保护。

---

## 1. 智能体一键部署协议 (Agent Deployment Protocol)

**[AI Agent 指示]**：如果你是正在阅读此文档的 AI 智能体（Trae Solo, Cursor, Claude Code, VS Code/Codex），请直接在控制台执行以下步骤来为此项目完成一键装配：

### 步骤一：环境核验
在终端执行以下命令，确保工作区路径处于 Windows 开发环境下：
```powershell
# 确认当前盘符与目录
Get-Location
```

### 步骤二：一键初始化部署
在项目根目录下直接调用 PowerShell 脚本。该脚本会自动检测当前目录、平铺部署 .venv 虚拟环境、在根目录下建立单一可信源 .env 配置文件，并自动激活跨 IDE 的元规则注入：
```powershell
powershell -ExecutionPolicy Bypass -File .\ai外挂工程\setup.ps1
```

### 步骤三：自愈验证
装配完成后，运行以下命令，验证是否能在完全免本地代理配置、不产生系统盘污染的前提下成功抓取海外目标：
```powershell
# 运行冒烟测试
.\.venv\Scripts\python.exe ai外挂工程/crawl_test.py
```

## 2. 跨 IDE 自适应共识 (Cross-IDE Registry)

本套件装配成功后，会自动检测并向你当前运行的 IDE 注入核心共识规则：

- **Claude Code (CLI 智能体)**：读取根目录 `CLAUDE.md` 获取项目指令与记忆裁剪。
- **VS Code / Copilot / Codex**：读取 `.vscode/copilot-instructions.md`。
- **Cursor**：读取 `.cursorrules`。
- **Trae**：读取 `.trae/rules/` 目录。

## 3. 环境配置规范 (.env)

主目录下唯一的配置文件 `.env` 规范模版如下（支持 mimo-v2.5 / DeepSeek / GPT-4o 四模型一键切换）：
```
LLM_MODEL="mimo-v2.5"
LLM_BASE_URL="https://token-plan-sgp.xiaomimimo.com/v1"
LLM_API_KEY="your-api-key-here"

# 隔离与重定向变量 (不可删除)
PLAYWRIGHT_BROWSERS_PATH="ai外挂工程/.playwright-browsers"
PIP_CACHE_DIR="ai外挂工程/.pip-cache"
```

---