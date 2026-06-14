# 项目长期记忆内核 (Project Memory Core)

> 智能体提示：在开始工作前，请先阅读此文件，了解项目现状。任务完成后，请更新此文件。

## 1. 核心技术栈 (Technology Stack)
- 语言：PowerShell + Python 3.10+
- 配置管理：python-dotenv ≥1.0.0（唯一依赖）
- 网页抓取：urllib（标准库）
- 规则文件：Markdown

## 2. 系统当前架构 (System Architecture)
```
├── setup.ps1          ← 一键启动
├── uninstall.ps1      ← 一键卸载
├── .env               ← 本地配置（已 Git 忽略）
├── docs/              ← 文档中心
│   ├── SPEC.md        ← 产品规格说明书
│   └── MEMORY.md      ← 本文件
├── src/               ← 核心代码
│   ├── 01_memory_core/    ← 记忆内核
│   └── 02_git_defender/   ← Git 安全守卫
└── tests/             ← 测试集（预留）
```

## 3. 配置规范
- **单一配置源**：根目录 `.env` 是唯一配置文件
- **配置加载**：所有脚本通过 `find_dotenv()` 向上追溯加载
- **安全隔离**：`.env` 已被 `.gitignore` 忽略

## 4. 已完工功能模块 (Completed Features)
- [x] 一键注入（Trae/VS Code/Cursor/Claude Code）
- [x] 安全隔离防线（.env 密钥保护）
- [x] 防爆量动态 Git 预提交钩子
- [x] 轻量自愈与免代理抓取

## 5. 当前开发断点 (Current Breakpoints)
- 上次开发停留在：MVP 1.0 目录标准化重构完成
- 待解决的卡点/Bug：无

## 6. 下一步行动计划 (Next Steps)
1. 根据实际项目需求，配置 LLM API Key
2. 运行 `setup.ps1` 完成环境初始化
3. 使用爬虫引擎抓取目标网站并生成报告
