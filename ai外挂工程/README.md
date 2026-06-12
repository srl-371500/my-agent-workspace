# AI 外挂工程 · Agent Sandbox Toolkit

零侵入的 AI 智能体开发工具箱：分层记忆内核 + Git 提交安全守卫 + 一键部署/无痕卸载。

## 快速开始

```bash
# 双击即可，兼容任何 IDE 终端 / Git Bash / PowerShell
setup.bat
```

部署后自动完成：`.venv` 创建 → 依赖安装 → `.env` 生成 → IDE 规则部署 → Git Hook 绑定。

## 配置模型

编辑 `.env`，一行切换任意 OpenAI-Compatible 模型：

```bash
LLM_MODEL="mimo-v2.5"
LLM_BASE_URL="https://token-plan-sgp.xiaomimimo.com/v1"
LLM_API_KEY="your-api-key-here"
```

已验证兼容：Mimo · DeepSeek (`deepseek-chat`) · GPT-4o · Claude (Anthropic 兼容网关)。

## 模块架构

| 模块 | 功能 |
|------|------|
| `01_memory_core/` | 分层记忆内核（SPEC 宪法 + CHRONICLE 滚动日志 + LLM 压缩归档） |
| `02_git_defender/` | Git pre-commit 钩子（敏感信息阻断 + Python 语法校验 + 动效审计 + 记忆自动归档） |
| `utils.py` | 统一工具库（LLM 路由 · JSON 修复 · 动效提取 · UTF-8 读写） |

## 跨 IDE 兼容

`setup.bat` 自动部署规则到 `.trae/rules/`、`.vscode/copilot-instructions.md`、`.cursorrules`，兼容：

- **Trae** (Solo / Cloud Code)
- **VS Code** + GitHub Copilot
- **Cursor**
- **JetBrains** + AI Assistant
- **Git Bash / PowerShell / CMD**

## 卸载

```bash
uninstall.bat
```

4 步无痕：恢复 Git Hook → 清理 IDE 规则 → 强杀占用进程 → 物理删除工具箱。MEMORY.md / SPEC.md / .gitignore 自动保留。

## 环境隔离

所有产物锁定在工具箱目录内，C 盘零污染：

| 产物 | 路径 |
|------|------|
| Python 虚拟环境 | `.venv/` |
| Playwright 浏览器 | `.playwright-browsers/` |
| pip 缓存 | `.pip-cache/` |
