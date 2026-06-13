# 项目长期记忆内核 (Project Memory Core)

> 智能体提示：在开始工作前，请先阅读此文件，了解项目现状。任务完成后，请更新此文件。

## 1. 核心技术栈 (Technology Stack)
- 语言：Python 3.10+
- 浏览器自动化：Playwright ≥1.40.0
- LLM 调用：OpenAI SDK ≥1.0.0
- 环境变量：python-dotenv ≥1.0.0
- HTTP 客户端：urllib (标准库) + httpx ≥0.25.0

## 2. 系统当前架构 (System Architecture)
- `ai外挂工程/`: 智能体沙箱武器库主目录（V2.0 扁平化架构）
  - `01_memory_core/`: 长期记忆内核（含爬虫引擎）
  - `02_git_defender/`: Git 提交防泄密拦截器
  - `setup.ps1`: 一键部署脚本（元规则注入 + 环境配置）

## 3. 配置规范
- **单一配置源**：根目录 `.env` 是唯一配置文件
- **配置加载**：所有脚本通过 `find_dotenv()` 向上追溯加载
- **隔离机制**：`PLAYWRIGHT_BROWSERS_PATH` 和 `PIP_CACHE_DIR` 定向到 `ai外挂工程/` 内部

## 4. 已完工功能模块 (Completed Features)
- [x] 记忆分层架构（SPEC.md + CHRONICLE.md + archive）
- [x] Git 安全守卫（pre-commit 钩子 + 敏感信息扫描）
- [x] 免代理降级抓取（urllib + 云端网关降级）
- [x] 多 IDE 元规则自适应注入（Trae/VS Code/Cursor/Claude）

## 5. 当前开发断点 (Current Breakpoints)
- 上次开发停留在：V2.0 架构重构完成
- 待解决的卡点/Bug：无

## 6. 下一步行动计划 (Next Steps)
1. 根据实际项目需求，配置 LLM API Key
2. 运行 `setup.ps1` 完成环境初始化
3. 使用爬虫引擎抓取目标网站并生成报告
