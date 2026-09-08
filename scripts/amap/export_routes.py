#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把行程导出为可导入高德地图/旅行软件的路线文件。

产出（写入 travel-site/data/export/ 与 site/export/）：
  1. trip-<slug>.kml  —— 高德地图 App「收藏→导入」/ Google 地球 / 两步路等可导入
  2. trip-<slug>.gpx  —— 通用轨迹格式（两步路/六只脚/运动 App）
  3. routes.json      —— 每日路线 polyline 缓存（供网站前端直接绘制）

说明：
  - 坐标来自高德（GCJ-02）：导入高德系 App 无偏移；导入 Google 地球等 WGS84 系会偏移，属正常坐标差异。
  - KML/GPX 只表达"路线图/标记"，高德官方不支持把行程直接写入对手方收藏，导入后可自行整理收藏。
"""
import json, os, sys, time, urllib.parse, urllib.request, xml.sax.saxutils as sax

KEY = os.environ.get("AMAP_WEB_KEY", "")
BASE = "https://restapi.amap.com/v3/direction"
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
TRIP_DIR = os.path.join(BASE_DIR, "data", "trips")
EXPORT_DIR = os.path.join(BASE_DIR, "data", "export")
SITE_EXPORT_DIR = os.path.join(BASE_DIR, "site", "export")


def esc(s):
    return sax.escape(str(s or ""))


def call_direction(mode, origin, dest):
    ep = {"driving": "driving", "walking": "walking", "transit": "transit/integrated"}.get(mode, "driving")
    params = {"origin": origin, "destination": dest, "strategy": 0, "extensions": "all", "key": KEY}
    url = f"{BASE}/{ep}?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(url, timeout=25) as r:
        return json.load(r)


def get_polyline(mode, a, b):
    o = f"{float(a['lng']):.6f},{float(a['lat']):.6f}"
    d = f"{float(b['lng']):.6f},{float(b['lat']):.6f}"
    res = call_direction(mode, o, d)
    if res.get("status") != "1":
        return None, o, d
    path = res["route"]["paths"][0]
    pts = []
    for step in path.get("steps", []):
        for p in (step.get("polyline") or "").split(";"):
            if p:
                lon, lat = p.split(",")[:2]
                pts.append([float(lon), float(lat)])
    return pts, o, d


def build(trip):
    by_id = {p["id"]: p for p in trip["pois"]}
    by_id.update({p["id"]: p for p in trip.get("restaurants", [])})
    by_id.update({p["id"]: p for p in trip.get("hotels", [])})
    meta = trip["meta"]
    slug = f"trip-{meta.get('slug', meta['destination'])}"
    days = []
    for day in trip.get("itinerary", []):
        seq = []
        for it in day.get("items", []):
            p = by_id.get(it.get("poiId"))
            if p and p.get("lat"):
                seq.append(p)
        mode = "walking" if "步行" in (day.get("dailyRoute", {}).get("mode") or "") else "driving"
        legs = []
        polyline_all = []
        for i in range(len(seq) - 1):
            pts, o, d = get_polyline(mode, seq[i], seq[i + 1])
            if pts:
                polyline_all.extend(pts)
            legs.append({"from": seq[i]["name"], "to": seq[i + 1]["name"], "polyline": pts, "origin": o, "dest": d})
            time.sleep(0.3)
        days.append({"day": day["day"], "date": day.get("date"), "theme": day.get("theme"),
                     "mode": mode, "points": [{"name": p["name"], "lng": p["lng"], "lat": p["lat"], "desc": p.get("notes", "")} for p in seq],
                     "legs": legs, "polyline": polyline_all})
    routes = {"slug": slug, "destination": meta["destination"], "days": days}
    return routes


def to_kml(routes):
    parts = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<kml xmlns="http://www.opengis.net/kml/2.2">',
             f"<Document><name>{esc(routes['destination'])} 行程路线图</name>"]
    for d in routes["days"]:
        day_name = f"Day{d['day']} {esc(d.get('theme', ''))} ({esc(d.get('date', ''))})"
        parts.append(f"<Folder><name>{day_name}</name>")
        for p in d["points"]:
            parts.append(
                f"<Placemark><name>{esc(p['name'])}</name><description>{esc(p.get('desc', ''))}</description>"
                f"<Point><coordinates>{p['lng']},{p['lat']},0</coordinates></Point></Placemark>")
        if len(d["polyline"]) > 1:
            coords = " ".join(f"{pt[0]},{pt[1]},0" for pt in d["polyline"])
            parts.append(
                f"<Placemark><name>{day_name} 路线</name><LineString><tessellate>1</tessellate>"
                f"<coordinates>{coords}</coordinates></LineString></Placemark>")
        parts.append("</Folder>")
    parts.append("</Document></kml>")
    return "\n".join(parts)


def to_gpx(routes):
    parts = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<gpx version="1.1" creator="travel-planner" xmlns="http://www.topografix.com/GPX/1/1">',
             f"<metadata><name>{esc(routes['destination'])} 行程路线图</name></metadata>"]
    for d in routes["days"]:
        for p in d["points"]:
            parts.append(f"<wpt lat=\"{p['lat']}\" lon=\"{p['lng']}\"><name>{esc(p['name'])}</name><desc>{esc(p.get('desc', ''))}</desc></wpt>")
        if len(d["polyline"]) > 1:
            parts.append(f"<trk><name>Day{d['day']} {esc(d.get('theme', ''))}</name><trkseg>")
            for pt in d["polyline"]:
                parts.append(f"<trkpt lat=\"{pt[1]}\" lon=\"{pt[0]}\"></trkpt>")
            parts.append("</trkseg></trk>")
    parts.append("</gpx>")
    return "\n".join(parts)


def main():
    os.makedirs(EXPORT_DIR, exist_ok=True)
    os.makedirs(SITE_EXPORT_DIR, exist_ok=True)
    out = []
    for f in sorted(sys.argv[1:] or glob_trips()):
        trip = json.load(open(f, encoding="utf-8"))
        routes = build(trip)
        kml = to_kml(routes)
        gpx = to_gpx(routes)
        for ext, content in (("kml", kml), ("gpx", gpx)):
            path = os.path.join(EXPORT_DIR, f"{routes['slug']}.{ext}")
            open(path, "w", encoding="utf-8").write(content)
            # 同步到 site/export 供构建时内嵌/部署
            open(os.path.join(SITE_EXPORT_DIR, f"{routes['slug']}.{ext}"), "w", encoding="utf-8").write(content)
        open(os.path.join(EXPORT_DIR, f"{routes['slug']}.routes.json"), "w", encoding="utf-8").write(json.dumps(routes, ensure_ascii=False, indent=1))
        out.append({"slug": routes["slug"], "days": len(routes["days"]), "points": sum(len(d["points"]) for d in routes["days"])})
        print(f"✅ {routes['slug']}: {len(routes['days'])} 天 / {sum(len(d['points']) for d in routes['days'])} 点 → KML+GPX+routes.json")
    return out


def glob_trips():
    import glob
    return sorted(glob.glob(os.path.join(TRIP_DIR, "trip-*.json")))


if __name__ == "__main__":
    main()