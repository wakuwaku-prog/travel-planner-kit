#!/usr/bin/env bash
# travel-planner-kit 一键发布脚本：提交绍兴行程 → 推送 → GitHub Pages 自动构建
# 用法：在 kit 目录下执行  bash deploy-site.sh   （或双击 deploy-site.cmd）
set -euo pipefail
cd "$(cd "$(dirname "$0")" && pwd)"

echo "== 1/3 添加行程相关文件 =="
git add data/trips/ guides/ data/research/ scripts/amap/fill_geo.py
# site/export 在 .gitignore 中，但网站「导入路线」面板需要它，强制入库
git add -f site/export/trip-shaoxing*.kml site/export/trip-shaoxing*.gpx site/export/trip-shaoxing*.routes.json 2>/dev/null || true
git status --short | head -15

echo "== 2/3 提交 =="
git commit -m "绍兴一日游行程（2026-10-06·上海出发·3人）：trip JSON + 攻略 + 调研数据

- B站 29 种子 / 5 核心视频全文转写
- 小红书 94 篇去重种子 / 8 篇高赞帖精读
- 12 个 web 来源交叉验证（含鲁迅故里官方预约规则）
- 备选点 9 个，站点由 CI 自动构建发布" || echo "（没有新变更可提交，直接尝试推送）"

echo "== 3/3 推送并触发 Pages 部署 =="
git push origin main

echo ""
echo "✅ 已推送，GitHub Actions 构建完成后（约 1-2 分钟）访问："
echo "   https://wakuwaku-prog.github.io/travel-planner-kit/"
echo "   构建进度：https://github.com/wakuwaku-prog/travel-planner-kit/actions"
