# 📜 项目宪法 (Project Constitution)

> 本文档为项目的核心技术契约，只存放静态技术栈、目录结构和核心规范。
> 限制在 1 页纸以内，严禁动态日志写入此文件。

---

## 1. 核心技术栈

| 层级 | 技术选型 | 版本要求 |
|------|---------|---------|
| **前端** | React + Vite + Tailwind CSS | Node.js >= 18 |
| **后端/工具** | Python + uv | Python >= 3.12 |
| **LLM 网关** | OpenAI 标准兼容接口 | 支持任意模型 |
| **浏览器自动化** | Playwright + browser-use | 最新版 |
| **数据验证** | Pydantic v2 | >= 2.0 |
| **环境管理** | python-dotenv | 最新版 |

---

## 2. 系统架构

```
my-agent-workspace/
├── 01_memory_core/              # 记忆系统
│   ├── SPEC.md                 # 项目宪法（静态）
│   └── .trae/rules/            # AI 行为约束规则
├── 02_git_defender/             # 安全系统
│   └── githooks/               # Git 钩子
├── 03_browser_crawler/          # 爬虫系统
├── .env.example                # 环境变量模板
├── .gitignore                  # Git 忽略规则
├── setup.ps1                   # 一键部署脚本
└── setup.bat                   # 双击启动器
```

---

## 3. 核心契约

### 3.1 Zero-Secrets 原则
- **禁止**：在代码或配置文件中硬编码 API Key
- **强制**：所有敏感信息通过 `.env` 环境变量注入
- **验证**：Git pre-commit 钩子自动检测并拦截

### 3.2 多模型兼容
- **接口标准**：OpenAI Chat Completions API
- **切换方式**：修改 `.env` 中的 `LLM_MODEL` 和 `LLM_BASE_URL`
- **支持模型**：mimo、Claude、GPT、Gemini 等

### 3.3 分层记忆
- **SPEC.md**：静态技术契约（1 页纸）
- **CHRONICLE.md**：动态任务日志（滚动窗口）
- **archive/**：历史归档（按月压缩）

### 3.4 自愈式爬虫
- **无选择器**：不使用 CSS 选择器，防止网页改版失效
- **Markdown 降维**：HTML → Markdown → LLM 分析
- **结构化输出**：Pydantic 约束 + 自动修复

---

## 4. 部署规范

### 4.1 首次部署
```powershell
.\setup.ps1
```

### 4.2 黄金底盘同步
```powershell
.\setup.ps1 -Sync
```

### 4.3 环境配置
```bash
cp .env.example .env
# 编辑 .env 填入真实配置
```

---

## 5. 安全规范

| 规则 | 说明 |
|------|------|
| `.env` 不入库 | `.gitignore` 强制忽略 `*.env` |
| `config/settings.yaml` 不入库 | 包含敏感配置 |
| `logs/` 不入库 | 可能包含调试信息 |
| `reports/` 不入库 | 生成的报告文件 |

---

## 6. 历史里程碑

> 此区域由 AI 自动维护，从 CHRONICLE.md 压缩归档

### 2026-06-08：项目初始化
- 完成四大核心任务：初始化、Hook、Cron、Token 审计
- 建立完整的 AI 自动化基础设施

### 2026-06-09：模块化重构
- 创建三大模块化功能手提箱
- 实现一键部署脚本

### 2026-06-10：主动装配化升级
- 创建 Trae 原生静默规则
- 实现一键自动装配

### 2026-06-10：2026 标准重构
- 实现 Zero-Secrets 去密钥化架构
- 建立分层记忆与自动压缩系统
- 实现自愈式无选择器爬虫

---

## Historical Milestones

### 2026-06-12: Chronicle Auto-Archive
- 初始化项目结构、配置 Git 钩子、安装 Playwright 浏览器、测试 API 连通性、编写数据蒸馏脚本、部署自动化定时任务。
