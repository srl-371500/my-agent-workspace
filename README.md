# AI 外挂工具包 (Agent Sandbox Toolkit)

> 一个能让你的 IDE AI 助手瞬间变聪明、守规矩、不写乱码、不泄露密钥的本地一键式配置外挂包。

---

## 快速开始

### 1. 一键部署
```powershell
powershell -ExecutionPolicy Bypass -File .\setup.ps1
```

### 2. 配置 API Key
编辑根目录下的 `.env` 文件，填入你的 LLM API Key。

### 3. 验证安装
```powershell
.\.venv\Scripts\python.exe src/01_memory_core/crawl_test.py
```

---

## 4 大核心功能

| 功能 | 说明 |
|------|------|
| **一键注入** | 自动向 Trae/VS Code/Cursor/Claude Code 写入 AI 行为规范 |
| **安全隔离** | 确保 `.env` 密钥永远不会被误提交到 GitHub |
| **Git 钩子** | 提交前自动检查是否包含密钥 |
| **免代理抓取** | 无需代理即可抓取海外网站 |

---

## 项目结构

```
├── setup.ps1          ← 一键启动
├── uninstall.ps1      ← 一键卸载
├── .env               ← 本地配置（已 Git 忽略）
├── docs/              ← 文档
├── src/               ← 核心代码
└── tests/             ← 测试集
```

---

## 支持的 IDE

- Trae
- VS Code / Copilot
- Cursor
- Claude Code

---

## 技术栈

- PowerShell（部署脚本）
- Python 标准库（urllib）
- python-dotenv（唯一依赖）
- Markdown（规则文件）

---

## 详细文档

- [产品规格说明书](docs/SPEC.md)
- [项目记忆](docs/MEMORY.md)

---

*版本：MVP 1.0*
