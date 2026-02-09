#!/bin/bash
# 自动保存脚本 - 放在项目根目录

echo "📦 自动保存中..."

# 添加所有更改
git add .

# 提交（如果有更改）
if git diff --cached --quiet; then
    echo "✅ 没有新更改"
else
    git commit -m "Auto-save: $(date '+%Y-%m-%d %H:%M')"
    git push
    echo "✅ 已保存并推送到 GitHub"
fi
