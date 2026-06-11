---
description: 当检测到 githooks 文件夹存在时激活
globs: ["githooks/**/*"]
---
# 安全守卫行为规范
1. 如果检测到本项目尚未绑定 git hook（可以通过检查 git config 判定），请主动在终端运行 `git config core.hooksPath githooks` 进行一键绑定。
2. 始终监控本地修改，确保 `.gitignore` 中包含并激活了针对 `config/settings.yaml` 的忽略排除。若发现没有，请主动提示用户或自动帮其追加到最底部。