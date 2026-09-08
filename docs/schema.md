# trip-*.json 数据模型

网站 / 路线 / 导出全部由 `data/trips/trip-<目的地>.json` 驱动。必填字段如下（示例用占位值，不含真实目的地数据）。

```jsonc
{
  "meta": {
    "destination": "示例市",            // 目的地名称（slug 请用拼音/英文）
    "slug": "demo",
    "dates": ["2026-01-01", "2026-01-02", "2026-01-03"],
    "days": 3,
    "departureCity": "示例出发地",
    "travelers": "2人",
    "budget": "舒适",                  // 穷游/舒适/富游
    "preferences": ["风光", "美食"],
    "pace": "均衡",                    // 休闲/均衡/特种兵
    "sources": { "videos": 10, "posts": 20 },
    "generatedAt": "2026-01-01",
    "status": "调研完成"
  },
  "sources": [
    { "id": "v01", "platform": "bilibili", "type": "video", "url": "…",
      "title": "…", "author": "…", "status": "已转写", "summary": "…", "used": true },
    { "id": "x01", "platform": "xiaohongshu", "type": "post", "url": "…",
      "title": "…", "author": "…", "likes": "1234", "used": false }
  ],
  "pois": [
    { "id": "p01", "category": "景点", "name": "示例景点", "address": "…",
      "lng": 116.0, "lat": 24.0, "day": 1, "slot": "上午", "durationMin": 120,
      "bookingRequired": false, "ticketPrice": "免费", "openHours": "全天",
      "tags": ["拍照"], "notes": "…", "sourceIds": ["v01"], "checked": true }
  ],
  "hotels":  [ { "id": "h01", "name": "…", "area": "…", "lng": 116.0, "lat": 24.0,
                 "priceRange": "¥300-600/晚", "recommend": true, "notes": "…" } ],
  "restaurants": [ { "id": "r01", "name": "…", "type": "…", "avgPrice": 50,
                     "lng": 116.0, "lat": 24.0, "dianpingKeyword": "…", "tips": "…" } ],
  "experiences": [ { "id": "e01", "name": "…", "where": "…", "durationMin": 90,
                     "price": "…", "bookingRequired": false, "bestFor": "…" } ],
  "itinerary": [
    { "day": 1, "date": "2026-01-01", "theme": "…", "area": "…",
      "items": [ { "poiId": "p01", "time": "09:00-12:00" } ],
      "dailyRoute": { "mode": "driving", "distanceKm": 0, "durationMin": 0, "note": "由 route_fill.py 回填" },
      "notes": "…" }
  ],
  "tips": {
    "weather": { "season": "…", "high": 30, "low": 18, "advice": "…" },
    "packing": ["…"],
    "bookings": [ { "item": "…", "how": "…", "deadline": "提前X天" } ],
    "transportSchedules": [ { "line": "…", "note": "…" } ],
    "safety": ["…"],
    "customs": ["…"]
  }
}
```

## 字段约定

- `poiId`/`sourceIds` 必须与同级 ID 一致，保证可追溯
- `lng/lat` 用 GCJ-02（高德系）；`route_fill.py` 与 `export_routes.py` 回填/导出时保持同一坐标系
- `checked` 为前端默认勾选；用户可在网站上取消（加入/移出当日路线）
- `meta.sources` 用于展示调研达标情况（videos ≥10、posts ≥20 为推荐线）
- 缺失可选字段用空字符串/空数组，脚本均有容错