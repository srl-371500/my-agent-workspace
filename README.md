# 🤖 智能体沙箱武器库 (Agent Sandbox Arsenal)

> **专为 AI 智能体设计的一键部署开发外挂套件**  
> 基于 Toolbox 子目录隔离架构，实现 C 盘零污染、D 盘完全隔离的沙箱环境

## 🎯 项目定位

本项目是一个**智能体开发外挂套件**，采用创新的 Toolbox 子目录隔离设计，为 AI 智能体提供：

- **一键部署**：单个命令完成完整开发环境搭建
- **完全隔离**：所有依赖、缓存、浏览器数据存储在 D 盘，C 盘零污染
- **智能防御**：内置 Git Hooks 敏感词阻断、代码审计机制
- **无痕卸载**：项目交付时完美清理，仅保留核心记忆文档
- **AI 友好**：专为 IDE 智能体（Trae、Cursor 等）优化的部署协议

## 🚀 AI 部署协议 (Agent Deployment Protocol)

**致 AI 智能体：** 如果你正在读取此 README，请按照以下协议执行部署：

### 1. 环境准备
```bash
# 确保在项目根目录（D:\my-agent-workspace）
cd D:\my-agent-workspace
```

### 2. 一键部署
```powershell
# 执行一键部署脚本（推荐）
.\setup.bat

# 或者使用 PowerShell 脚本
.\setup.ps1
```

### 3. 部署内容
执行上述命令后，系统将自动完成：
- ✅ **D 盘隔离装配**：创建 `.venv`、`.playwright-browsers` 等目录到 D 盘
- ✅ **Git Hooks 绑定**：配置 `core.hooksPath` 指向安全审计钩子
- ✅ **环境变量配置**：自动生成 `.env` 文件并设置 `PLAYWRIGHT_BROWSERS_PATH`
- ✅ **依赖安装**：使用清华镜像源安装 Python 依赖
- ✅ **浏览器部署**：自动安装 Chromium 浏览器到 D 盘隔离目录

### 4. 验证部署
```bash
# 检查 Git 钩子配置
git config core.hooksPath

# 应该输出：ai外挂工程/02_git_defender/githooks

# 检查环境变量
cat .env | grep PLAYWRIGHT_BROWSERS_PATH

# 应该输出：PLAYWRIGHT_BROWSERS_PATH="D:\.cache"
```

## 🗑️ 无痕卸载协议 (Teardown Protocol)

**致 AI 智能体：** 当项目交付需要清理环境时，请执行以下协议：

### 1. 执行无痕卸载
```powershell
# 执行一键卸载脚本
.\ai外挂工程\uninstall.bat

# 或者使用 PowerShell 脚本
.\ai外挂工程\uninstall.ps1
```

### 2. 卸载内容
执行卸载脚本后，系统将自动完成：
- ✅ **Git 环境还原**：移除 `core.hooksPath` 配置
- ✅ **IDE 规则清理**：删除 `.trae/` 目录
- ✅ **敏感信息清除**：删除 `.env` 文件（包含 API 密钥）
- ✅ **虚拟环境清理**：删除 `.venv/` 目录
- ✅ **工具套件自毁**：物理删除 `ai外挂工程/` 目录
- ✅ **记忆文档保留**：**完美留存** `MEMORY.md`、`SPEC.md`、`.gitignore`

### 3. 卸载后状态
```
✅ Git Hook 已还原
✅ .trae 规则已卸载
✅ MEMORY.md / SPEC.md / .gitignore 安全保留
✅ 工具套件沙箱已物理粉碎
```

## ⚙️ 环境变量配置

### 配置规范
项目使用 `.env` 文件管理环境变量，**必须**声明以下关键配置：

```bash
# 必须配置：浏览器安装路径（保护 C 盘）
PLAYWRIGHT_BROWSERS_PATH="D:\.cache"

# 推荐配置：Python 缓存路径
PIP_CACHE_DIR="D:\.cache\pip"

# 推荐配置：Pyppeteer 缓存路径
PYPPETEER_HOME="D:\.cache\pyppeteer"
```

### 配置模板
参考 `.env.example` 文件，包含：
- LLM 模型配置（支持 OpenAI、Claude、小米等）
- 代理配置
- 日志级别配置
- 缓存路径配置

### 安全规范
- **禁止**在 `.env` 中存储真实 API 密钥
- **必须**使用 `your-api-key-here` 占位符
- **必须**将 `.env` 添加到 `.gitignore`

## 📦 模块架构

### 01_memory_core - 记忆核心系统
- **功能**：智能体长期记忆管理
- **文件**：`MEMORY.md`、`CHRONICLE.md`、`SPEC.md`
- **特性**：记忆归档、版本追踪、模板生成

### 02_git_defender - Git 防御模块
- **功能**：代码提交安全审计
- **文件**：`pre-commit`、`pre-commit-audit.py`
- **特性**：敏感词阻断、代码规范检查、安全审计

### 03_browser_crawler - 浏览器爬虫模块
- **功能**：自动化浏览器操作
- **依赖**：Playwright、Browser-Use
- **特性**：无头浏览器、反检测、数据提取

## 🔧 使用示例

### 智能体部署流程
```python
# 示例：Trae 智能体自动部署
import subprocess

# 1. 检查环境
result = subprocess.run(["git", "config", "core.hooksPath"], capture_output=True)
if "ai外挂工程" not in result.stdout.decode():
    # 2. 执行部署
    subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", ".\setup.ps1"])
    
# 3. 验证部署
print("✅ 部署完成，环境已就绪")
```

### 项目交付流程
```python
# 示例：项目交付时的清理
import subprocess

# 1. 执行无痕卸载
subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", ".\ai外挂工程\uninstall.ps1"])

# 2. 验证清理结果
print("✅ 环境已清理，仅保留核心记忆文档")
```

## ⚠️ 注意事项

### 安全警告
- **绝对不要**将真实 API 密钥提交到 Git 仓库
- **绝对不要**在 C 盘创建虚拟环境或缓存目录
- **绝对不要**禁用 Git Hooks 安全审计

### 最佳实践
- 始终使用 D 盘路径进行缓存配置
- 定期执行 `pip cache purge` 清理 Python 缓存
- 项目交付时必须执行无痕卸载

### 故障排除
1. **部署失败**：检查 Python 版本（需要 3.8+）
2. **Git 钩子不工作**：运行 `git config core.hooksPath ai外挂工程/02_git_defender/githooks`
3. **浏览器安装失败**：检查网络连接，或手动下载 Chromium

## 📊 系统要求

- **操作系统**：Windows 10/11
- **Python**：3.8 或更高版本
- **Git**：2.30 或更高版本
- **磁盘空间**：D 盘至少 2GB 可用空间
- **网络**：需要访问 PyPI 和浏览器下载源

## 🎉 成功指标

部署成功的标志：
- ✅ `git config core.hooksPath` 输出包含 `ai外挂工程`
- ✅ `.env` 文件包含 `PLAYWRIGHT_BROWSERS_PATH="D:\.cache"`
- ✅ `.venv` 目录存在于项目根目录
- ✅ `.playwright-browsers` 目录存在于 D 盘缓存路径

---

**🚀 开始部署：** `.\setup.bat`  
**🗑️ 无痕卸载：** `.\ai外挂工程\uninstall.bat`  
**📖 完整文档：** 阅读 `必须看的内容_系统交接与迁移说明.md`