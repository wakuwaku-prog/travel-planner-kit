# travel-research — 旅行调研与行程网站生成技能（通用模板）

> 定位：一次会话内完成「询问用户 → 三平台调研 → 结构化攻略 → 高德地图补齐 → 生成网站 → 导出路线」。
> 配合仓库 https://github.com/wakuwaku-prog/travel-planner-kit 使用；本技能可复制到 `~/.dsh/skills/travel-research/` 固化复用。

## 触发词

- "帮我规划旅行/做攻略/做行程"
- "想去 X 玩 N 天"
- "做个旅行网站"

## 输入收集（第一步，选项化提问）

必须收集：目的地、天数、出发日期、出发城市、人数、预算档位（穷游/舒适/富游）、内容偏好（可多选）、节奏（休闲/均衡/特种兵）。

## 调研阶段（第二步）

| 平台 | 最少数量 | 工具 |
|---|---|---|
| 小红书 | 20 篇 | `agent-reach`（OpenCLI/CDP 或 xhs cookies）；直接访问 `search_result?keyword=` 路由；多关键词采集后去重；用 `opencli xiaohongshu note <完整URL含xsec_token>` 精读高赞帖 |
| B站等视频 | 10 个视频 | `bili search` 收集种子（≥10），选 3-5 个核心视频用 yt-dlp 下载音频 + faster-whisper 转写，提炼要点 |
| 补充 | 按需 | exa-search / parallel-web：官网、交通时刻、预约规则、天气 |

产出：
1. `data/raw/` 原始记录（字幕文本、搜索结果 JSON）
2. LLM 综合 → `guides/<目的地>-攻略.md`
3. 提炼 → `data/research/`（种子与笔记）+ **`data/trips/trip-<目的地>.json`**

## 结构化与地图补齐（第三步）

1. 提炼 `pois/hotels/restaurants/experiences` 及逐日行程草案进 trip JSON；
2. 高德 Web 服务回填坐标/POI ID/天气：
   - `/config/district` 校验目的地；`/geocode/geo` + `/place/text` 回填实体（**LLM 生成名不可信，坐标以高德回填为准**）；
   - `/weather/weatherInfo` 写 `tips.weather`；
3. `python scripts/amap/route_fill.py data/trips/trip-*.json` → 逐日真实距离/耗时回写；
4. `python scripts/amap/export_routes.py data/trips/trip-*.json` → KML/GPX 路线导出。

## 生成网站与导出路线（第四步）

1. `python scripts/build_site.py` → `site/index.html`（7 栏目：行程/景点指南/特色体验/餐饮指南/出发前准备/旅行提醒/资料来源 + 📦 导入路线）；
2. 地图：高德 JS API 画每日路线；每 POI「跳转高德导航」＝ `https://uri.amap.com/navigation?to=<lng>,<lat>,<名称>&mode=car&callnative=1`；
3. 交互：用户勾选感兴趣景点 → 前端 `AMap.Driving.search` 动态重规划；
4. **导入高德/旅行软件**：网站「导入路线」面板提供 KML（高德 App 收藏→导入）与 GPX（两步路等）下载 + 每日整体路线链接/二维码；
5. 汇报：网站位置 + 调研统计（视频/帖子数量）+ 关键提醒 + 来源。

## 硬规则

- 每条攻略信息尽量挂 `sourceIds` 可追溯；≥2 个独立来源交叉验证才进"确定"栏
- 票/价/营业信息标注"规划估算，出发前以官方为准"
- 不为名店扭曲路线：餐厅是当天区域的顺路候选
- 一天一个主区域；行程是参考坐标，不是逐小时执行脚本
- 不保存证件/订单号/完整聊天记录；长期偏好写入记忆文件（如 `~/.travel-research/MEMORY.md`）
- 高德 Key 只写 `.env`（gitignore），汇报里不出现明文；获取 Key 的官方教程（创建项目与 Key）：https://lbs.amap.com/api/mcp-server/create-project-and-key