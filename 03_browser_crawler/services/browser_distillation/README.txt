========================================
browser_distillation 数据蒸馏服务说明
========================================

【文件夹作用】
本文件夹是基于 browser-use 和 mimo-v2.5 的无人值守多模态爬虫与数据蒸馏服务。

功能：自动打开浏览器访问指定网站，使用 AI 视觉模型分析网页内容，生成结构化报告。

----------------------------------------
核心文件功能
----------------------------------------

1. analyze_portfolio.py   - 爬取主脚本
   - 使用 browser-use 框架控制浏览器
   - 调用 mimo-v2.5 多模态视觉模型分析网页截屏
   - 生成分析报告到 reports/ 目录
   - 记录 Token 消耗到 logs/ 目录

2. cost_audit.py          - 计费模块
   - calculate_cost()    - 计算 Token 成本
   - record_audit()      - 记录审计日志
   - print_cost_summary() - 打印成本摘要

3. run_distillation.bat   - 一键双击手动运行脚本
   - 双击即可运行分析任务
   - 自动设置环境变量和工作目录

4. register_cron.ps1      - 定时任务注册脚本
   - 注册 Windows 任务计划程序定时任务
   - 默认每天上午 9:00 自动运行

5. test_minimal.py        - API 连通性测试脚本
   - 测试 MiMo-V2.5 API 是否正常
   - 测试 Playwright 浏览器是否正常

6. .venv/                 - Python 虚拟环境
   - 包含所有依赖包
   - 使用 uv 管理

7. pyproject.toml         - Python 项目配置
   - 定义依赖和项目元信息

----------------------------------------
运行与配置指南
----------------------------------------

【手动执行命令】

方法 1：双击运行
  直接双击 run_distillation.bat 文件

方法 2：命令行运行
  cd services\browser_distillation
  uv run python analyze_portfolio.py

方法 3：测试 API 连通性
  cd services\browser_distillation
  uv run python test_minimal.py

----------------------------------------
【注册 Windows 定时任务】

前提条件：
  - 必须以管理员身份运行 PowerShell
  - 必须先 cd 到项目根目录

步骤：

1. 以管理员身份打开 PowerShell
   （右键点击 PowerShell -> 以管理员身份运行）

2. 切换到项目根目录：
   cd D:\my-agent-workspace

3. 运行注册脚本：
   .\services\browser_distillation\register_cron.ps1

4. 看到 [SUCCESS] 提示即为注册成功

注册后的任务详情：
  - 任务名称：BrowserDistillation_DailyAnalysis
  - 触发时间：每天上午 9:00
  - 执行程序：.venv\Scripts\python.exe
  - 执行参数：analyze_portfolio.py
  - 工作目录：D:\my-agent-workspace\services\browser_distillation

----------------------------------------
【管理 Windows 定时任务】

查看任务状态：
  Get-ScheduledTask -TaskName "BrowserDistillation_DailyAnalysis"

立即运行任务（测试用）：
  Start-ScheduledTask -TaskName "BrowserDistillation_DailyAnalysis"

暂停任务：
  Disable-ScheduledTask -TaskName "BrowserDistillation_DailyAnalysis"

恢复任务：
  Enable-ScheduledTask -TaskName "BrowserDistillation_DailyAnalysis"

删除任务：
  Unregister-ScheduledTask -TaskName "BrowserDistillation_DailyAnalysis"

在任务计划程序 GUI 中查找：
  1. 按 Win 键，搜索"任务计划程序"
  2. 打开任务计划程序
  3. 在左侧点击"任务计划程序库"
  4. 在中间列表中找到 "BrowserDistillation_DailyAnalysis"
  5. 右键点击可以运行、禁用、删除、查看属性

----------------------------------------
环境配置
----------------------------------------

API 配置文件：..\..\config\settings.yaml
  endpoint: https://token-plan-sgp.xiaomimimo.com/v1
  model: mimo-v2.5
  api_key: 你的 API 密钥

环境变量：
  BROWSER_USE_DISABLE_EXTENSIONS=true
  （已在 run_distillation.bat 中自动设置）

----------------------------------------
输出文件
----------------------------------------

分析报告：..\..\reports\portfolio_inspiration_report.md
审计日志：..\..\logs\cost_audit.json

----------------------------------------
依赖列表
----------------------------------------

browser-use >= 0.12.9    # 浏览器自动化框架
langchain-openai         # OpenAI 兼容接口
pyyaml                   # YAML 配置解析
playwright               # 浏览器驱动

----------------------------------------
常见问题
----------------------------------------

Q: 运行时提示 "Python was not found"
A: 使用 uv run python 而不是直接 python

Q: 浏览器启动超时
A: 确保设置了 BROWSER_USE_DISABLE_EXTENSIONS=true

Q: API 调用失败
A: 检查 config/settings.yaml 中的 api_key 和 endpoint

Q: 定时任务没有运行
A: 检查任务计划程序中任务是否被禁用，查看历史运行记录

========================================
