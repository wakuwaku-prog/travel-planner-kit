# travel-planner-kit — 通用旅行规划网站模板

> 一套「调研 → 攻略 → 高德路线 → 可部署网站」的完整方法包。**不含任何具体目的地数据**，拿到即可规划任意目的地。
> 由厦门实战项目沉淀（https://github.com/wakuwaku-prog/travel-site 是厦门实例仓库，含产出的数据与攻略）。

## 它能干什么

输入一次行程参数（目的地 / 天数 / 出发日期 / 出发地 / 人数 / 预算档位 / 偏好 / 节奏），Agent 按本模板内置的 `SKILL.md` 流程自动完成：

1. **调研**：`agent-reach`（小红书 ≥20 篇、B站/其他平台 ≥10 个视频，含字幕转写要点）＋ Exa 等补充
2. **整理**：攻略 Markdown + 结构化 `data/trips/trip-<目的地>.json`（行程/酒店/交通/特色/美食/项目 + 来源追溯）
3. **地图**：高德 API 补齐坐标与逐日实测路线（`route_fill.py`）
4. **导出**：生成 **KML / GPX** 路线文件 + 每日「一键唤起高德导航」链接（`export_routes.py`）
5. **建站**：生成 7 栏目可交互单页站（行程 / 景点指南 / 特色体验 / 餐饮指南 / 出发前准备 / 旅行提醒 / 资料来源 + 导入路线），带高德地图与每点导航按钮（`build_site.py`）
6. **部署**：GitHub Actions 自动发布到 GitHub Pages（模板自带 workflow）

## 目录结构

```text
travel-planner-kit/
├── README.md                  # 本文件
├── SKILL.md                   # travel-research 技能（Agent 工作流）
├── config.example.json        # 配置模板（→ 复制为 config.json）
├── .env.example※              # 高德 Key 放 .env（不入库）
├── docs/
│   └── schema.md              # trip-*.json 数据模型说明
├── data/
│   ├── trips/                 # ★ 行程数据（Agent 调研后生成，一个目的地一个文件）
│   ├── research/              # 调研中间产物（小红书种子、B站种子、POI 缓存）
│   ├── raw/                   # 原始素材（字幕、音频——已 gitignore）
│   └── export/                # KML/GPX/routes.json 导出物
├── scripts/
│   ├── build_site.py          # trip JSON → site/ 网站
│   └── amap/
│       ├── route_fill.py      # 逐日高德方向 API → 距离/耗时回填
│       └── export_routes.py   # KML/GPX + polyline 路线导出
├── site/                      # 生成后的网站（部署物）
└── .github/workflows/deploy-pages.yml
```

## 快速上手（5 步）

```bash
# 1. 配置（一次性）
cp config.example.json config.json    # 按需改
# 高德 Key 写入 .env：
#   AMAP_WEB_KEY=你的Web服务Key
#   AMAP_JS_KEY=你的JS API Key（需在控制台加部署域名白名单）

# 2. 调研（由 Agent 执行，按 SKILL.md）
#    告知：目的地/天数/出发日期/出发地/人数/预算/偏好/节奏
#    → 产出 data/trips/trip-<目的地>.json 与 guides/*.md

# 3. 高德路线回填（依赖 .env 里的 AMAP_WEB_KEY）
python scripts/amap/route_fill.py data/trips/trip-*.json

# 4. 导出可导入高德的路线图（KML/GPX）
python scripts/amap/export_routes.py data/trips/trip-*.json
#   → data/export/trip-*.kml / .gpx / .routes.json，site/export/ 同步

# 5. 生成网站
python scripts/build_site.py
#   → site/index.html（无数据时会生成说明页）

# 6. 部署（可选，模板自带 GitHub Actions）
git push origin main   # 自动构建并发布到 GitHub Pages
```

## 作为 Agent Skill 复用（免配置）

把 `SKILL.md` 复制到 `~/.dsh/skills/travel-research/SKILL.md`（或 Claude Code 的 `~/.claude/skills/`）。之后对 Agent 说「用 travel-research 规划一次 X 地 N 天行程」，Agent 会自动按流程调研并产出本仓库可消费的数据。需要的最小外部配置：

- 高德 Key（Web 服务 + JS API）→ `.env`
- 小红书：OpenCLI + Chrome 扩展（登录态）或 `agent-reach configure xhs-cookies`
- B站字幕/转写：faster-whisper 本地（模板脚本不依赖第三方付费 API）

## 数据模型

见 [docs/schema.md](docs/schema.md)。核心是 `data/trips/trip-<目的地>.json`，网站/路线/导出全部由它驱动；所有内容带 `sourceIds` 可追溯。

## 高德 API 清单（本模板实际调用）

| API | 用途 |
|---|---|
| `GET /v3/geocode/geo`、`/v3/config/district` | 地址→坐标、目的地校验 |
| `GET /v3/place/text` | POI 搜索（景点/餐厅/酒店真实候选） |
| `GET /v3/direction/driving`、`walking`、`transit/integrated` | 逐日路线（距离/耗时/polyline） |
| `GET /v3/weather/weatherInfo` | 目的地天气预报 |
| JS API `AMap.Driving`/`Polyline` | 网站前端画每日路线 |
| `uri.amap.com/navigation` | 每个点位「一键唤起高德 App 导航」 |

## 关于"行程导入高德"的说明（重要）

- **推荐用它来做线路图**：网站「行程」页地图就是**带编号+地名标注的逐日线路图**（每个景点有编号与名称，可直接点站唤起高德导航；手机端地图置顶吸顶 + 底部「顺序导航」栏逐站前进）。这是比导入高德更直观的方式。
- **高德 App「轨迹导入」的局限**：高德把 KML/GPX 当<u>运动轨迹</u>解析，**只画出一条路线、不显示各处地名**（把文件导入"足迹/记录"参考可以，但看不到名称）；且官方不支持第三方直接写入用户收藏。
- **逐段导航**：网站「导入路线」面板提供**每一段起点→终点**的高德导航链接（带地名），以及每天整体路线链接 + 二维码；手机直接点即唤起高德 App 导航。
- **分日 KML/GPX**：导出物含 `trip-<目的地>.kml/gpx`（全部）和 `trip-<目的地>-day<N>.kml/gpx`（逐日），便于分批导入查看。
- 坐标来自高德（GCJ-02）：导入高德系 App 无偏移；导入 Google 地球等 WGS84 工具会有系统偏差，属正常坐标差异。
- 高德官方不支持第三方直接把行程写入用户收藏，KML 中转 / 逐段导航是目前通用做法。

## 与厦门实例仓库的关系

- 本仓库 = 方法/模板（无目的地数据）
- https://github.com/wakuwaku-prog/travel-site = 用本方法生成的厦门行程实例（含完整数据与线上站：https://wakuwaku-prog.github.io/travel-site/）

## 许可

MIT（方法沉淀，数据与内容归各来源平台/作者所有）