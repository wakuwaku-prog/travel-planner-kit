#!/usr/bin/env bash
# travel-planner-kit 一键发布脚本：提交指定行程（slug）→ 推送 → GitHub Pages 自动构建
# 用法：bash deploy-site.sh <slug> ["<commit 标题>"]
#   例：bash deploy-site.sh dongji "东极岛 3 天 2 晚（2026-10-29·上海出发·单人）：trip JSON + 攻略 + 调研数据"
# 说明：
#   - 只添加该 slug 相关的文件（trip JSON / 攻略 / 调研种子 / 导出物），
#     避免误提交目录里其他会话的行程文件。
#   - 工具的修补（scripts/ 下）请先自行确认再手动 git add，本脚本不代劳。
set -euo pipefail
cd "$(cd "$(dirname "$0")" && pwd)"

SLUG="${1:?用法: bash deploy-site.sh <slug> [commit标题]}"
TITLE="${2:-行程更新：$SLUG}"

echo "== 1/3 添加 $SLUG 相关文件 =="
git add "data/trips/trip-${SLUG}-"*.json 2>/dev/null || true
git add "data/trips/trip-${SLUG}.json" 2>/dev/null || true
git add "guides/"*"-${SLUG}-攻略.md" 2>/dev/null || true
git add "data/research/"*"-${SLUG}"*.json 2>/dev/null || true
# site/export 在 .gitignore 中，但网站「导入路线」面板需要它，强制入库
git add -f "site/export/trip-${SLUG}"*.kml "site/export/trip-${SLUG}"*.gpx "site/export/trip-${SLUG}"*.routes.json 2>/dev/null || true
git status --short | head -20

echo "== 2/3 提交 =="
if git diff --cached --quiet 2>/dev/null; then
  echo "（暂存区为空：没有新变更可提交，直接尝试推送）"
else
  git commit -m "$TITLE"
fi

echo "== 3/3 推送并触发 Pages 部署 =="
# 全局代理（127.0.0.1:7890）未运行时自动直连兜底
git push origin main || {
  echo "（代理连接失败，改用直连重试）"
  git -c http.proxy= -c https.proxy= push origin main
}

echo ""
echo "✅ 已推送，GitHub Actions 构建完成后（约 1-2 分钟）访问："
echo "   https://wakuwaku-prog.github.io/travel-planner-kit/"
echo "   构建进度：https://github.com/wakuwaku-prog/travel-planner-kit/actions"
