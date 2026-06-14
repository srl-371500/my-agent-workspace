# AI 外挂工具包 - 产品规格说明书 (SPEC.md)

> 一句话说明：**一个能让你的 IDE AI 助手瞬间变聪明、守规矩、不写乱码、不泄露密钥的本地一键式配置外挂包。**

---

## 产品概述

你有没有遇到过这些问题？
- AI 助手每次开新对话就"失忆"，忘记之前做过什么
- AI 助手写的代码风格混乱，不符合你的项目规范
- 不小心把 API Key 提交到 GitHub，被坏人盗用
- 需要抓取海外网站，但本地没有代理工具

**这个工具包就是为了解决这些问题而生的。**

---

## 4 大核心功能

### 功能 1：一键注入（IDE Meta-Rules Injection）

**是什么**：运行一次脚本，自动向你的 IDE 写入一套"AI 行为规范"。

**输入**：
- 运行命令：`powershell -ExecutionPolicy Bypass -File .\setup.ps1`

**输出**：
- Trae IDE：自动写入 `.trae/rules/memory-agent.md`
- VS Code / Copilot：自动写入 `.vscode/copilot-instructions.md`
- Cursor：自动写入 `.cursorrules`
- Claude Code：自动写入 `CLAUDE.md`

**成功标准**：
- 运行后无报错
- 各 IDE 配置文件已生成
- AI 助手能读取到项目规范

---

### 功能 2：安全隔离防线（Security Isolation）

**是什么**：确保你的密钥永远不会被误提交到 GitHub。

**输入**：
- 项目根目录下的 `.env` 文件（包含 API Key）

**输出**：
- `.gitignore` 自动忽略 `.env` 文件
- 虚拟环境 `.venv` 被隔离在项目目录内
- 编译缓存不会污染系统盘

**成功标准**：
- 运行 `git check-ignore .env` 输出 `.env`
- 运行 `git ls-files .env` 无输出（未被跟踪）
- `.venv` 目录在项目根目录下，不在 C 盘

---

### 功能 3：防爆量动态 Git 预提交钩子（Smart Pre-commit Hook）

**是什么**：每次提交代码前，自动检查是否包含密钥。

**输入**：
- 执行 `git commit` 命令

**输出**：
- 如果检测到密钥：阻止提交，显示警告
- 如果安全：正常提交

**成功标准**：
- 提交包含 API Key 的文件时被阻止
- 提交正常代码时无阻碍
- 钩子能自动找到项目根目录（支持任意深度嵌套）

---

### 功能 4：轻量自愈与免代理抓取（Low-Cost Parsing & Crawling）

**是什么**：无需代理即可抓取海外网站，自动修复破损的 JSON。

**输入**：
- 运行命令：`.\.venv\Scripts\python.exe src/01_memory_core/crawl_test.py https://example.com`

**输出**：
- 抓取报告保存在 `reports/` 目录
- 自动检测页面中的动画库（GSAP、Lottie 等）

**成功标准**：
- 能成功抓取海外网站（如 apple.com）
- 无需配置代理
- 生成可读的 Markdown 报告

---

## 技术栈声明

**核心原则：零重量级依赖**

| 组件 | 技术选型 | 说明 |
|------|----------|------|
| 脚本语言 | PowerShell | 一键部署和清理 |
| 配置管理 | python-dotenv | 唯一依赖 |
| 网页抓取 | urllib（标准库） | 无需额外安装 |
| 规则文件 | Markdown | 人类可读可编辑 |

**依赖极简**：
```
python-dotenv>=1.0.0
```

---

## 项目结构

```
D:\my-agent-workspace\
│
├── setup.ps1              ← 一键启动脚本
├── uninstall.ps1          ← 一键自毁脚本
├── .env                   ← 本地私有配置（已 Git 忽略）
├── .gitignore             ← Git 忽略规则
├── README.md              ← 项目说明
│
├── docs/                  ← 文档中心
│   ├── SPEC.md            ← 本文件（产品规格说明书）
│   └── MEMORY.md          ← 项目记忆文件
│
├── src/                   ← 核心代码
│   ├── 01_memory_core/    ← 记忆内核
│   │   ├── utils.py       ← 工具库
│   │   ├── archive_chronicle.py  ← 记忆归档
│   │   └── crawl_test.py  ← 爬虫测试
│   │
│   └── 02_git_defender/   ← Git 安全守卫
│       └── githooks/
│           ├── pre-commit          ← Git 钩子
│           └── pre-commit-audit.py ← 审计脚本
│
└── tests/                 ← 测试集（预留）
```

---

## 使用流程

### 首次使用
1. 克隆或下载本项目
2. 打开 PowerShell，进入项目目录
3. 运行：`powershell -ExecutionPolicy Bypass -File .\setup.ps1`
4. 编辑 `.env` 文件，填入你的 API Key
5. 完成！

### 日常使用
- 正常开发，AI 助手会自动遵循注入的规范
- 提交代码时，Git 钩子会自动检查安全性
- 需要抓取网页时，运行爬虫脚本

### 卸载
- 运行：`powershell -ExecutionPolicy Bypass -File .\uninstall.ps1`
- 所有注入的规则和临时文件会被清除

---

## 常见问题

**Q: 这个工具会收集我的数据吗？**
A: 不会。所有数据都在本地，不会上传到任何服务器。

**Q: 支持哪些 IDE？**
A: Trae、VS Code、Cursor、Claude Code。

**Q: 需要安装 Python 吗？**
A: 是的，需要 Python 3.10+。脚本会自动创建虚拟环境。

**Q: 能抓取哪些网站？**
A: 任何公开网站。如果直连失败，会自动使用云端网关降级。

---

*最后更新：2025年*
*版本：MVP 1.0*
