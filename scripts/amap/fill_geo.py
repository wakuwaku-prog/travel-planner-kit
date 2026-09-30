#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""为 trip JSON 中的 pois/hotels/restaurants 回填高德坐标/POI ID/地址，并拉取天气预报。

坐标一律来自高德（GCJ-02），不信任 LLM 生成的坐标。
- 有 geoQuery 的走 /v3/place/text（citylimit 南京），命中即写入 lng/lat/poiId/address
- 失败则用 geoFallback 再试一次，仍失败再用 /v3/geocode/geo 兜底（此时无 poiId）
- 天气 /v3/weather/weatherInfo extensions=all 写回 tips.weather.advice
用法：AMAP_WEB_KEY=xxx python scripts/amap/fill_geo.py data/trips/trip-nanjing-2026-10-02.json
"""
import json, os, sys, time, urllib.parse, urllib.request

KEY = os.environ.get("AMAP_WEB_KEY", "")
BASE = "https://restapi.amap.com/v3"
CITY = "025"  # 南京 citycode


def req(path, params):
    params = {"key": KEY, **params}
    url = f"{BASE}{path}?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(url, timeout=20) as r:
        return json.load(r)


def place_text(kw):
    d = req("/place/text", {"keywords": kw, "city": CITY, "citylimit": "true", "offset": 3})
    if d.get("status") == "1" and d.get("pois"):
        p = d["pois"][0]
        return {"lng": p["location"].split(",")[0], "lat": p["location"].split(",")[1],
                "poiId": p.get("id", ""), "address": p.get("address", "") or p.get("pname", "") + p.get("cityname", "")}
    return None


def geocode(addr):
    d = req("/geocode/geo", {"address": addr, "city": CITY})
    if d.get("status") == "1" and d.get("geocodes"):
        loc = d["geocodes"][0]["location"]
        return {"lng": loc.split(",")[0], "lat": loc.split(",")[1], "poiId": "", "address": ""}
    return None


def fill_one(obj):
    if str(obj.get("lng", "")).strip() and str(obj.get("lat", "")).strip():
        return "已有坐标，跳过"
    for kw in (obj.get("geoQuery"), obj.get("geoFallback")):
        if not kw:
            continue
        r = place_text(kw)
        time.sleep(0.35)
        if r:
            obj["lng"], obj["lat"] = r["lng"], r["lat"]
            if r["poiId"]:
                obj["poiId"] = r["poiId"]
            if r["address"] and not obj.get("address"):
                obj["address"] = r["address"]
            return f"命中: {kw} -> ({r['lng']},{r['lat']})"
    if obj.get("address"):
        r = geocode(obj["address"])
        time.sleep(0.35)
        if r:
            obj["lng"], obj["lat"] = r["lng"], r["lat"]
            return f"地理编码兜底: {obj['address']} -> ({r['lng']},{r['lat']})"
    return "!! 未命中，需人工处理"


def fill_weather(trip):
    d = req("/weather/weatherInfo", {"city": "320100", "extensions": "all"})
    time.sleep(0.35)
    if d.get("status") != "1" or not d.get("forecasts"):
        return "天气查询失败: " + d.get("info", "")
    fc = d["forecasts"][0]
    lines = []
    for cast in fc.get("casts", []):
        lines.append(f"{cast['date']} {cast['dayweather']}转{cast['nightweather']} {cast['daytemp']}~{cast['nighttemp']}°C")
    advice = ("高德实时预报：" + "；".join(lines) +
              "。10月初南京早晚凉、适合徒步，带薄外套；若预报有雨改带雨衣（山顶风大伞不便）；"
              "出发前1天再刷新一次预报，10.4返程日天气以临近预报为准。")
    w = trip["tips"]["weather"]
    w["advice"] = advice
    if lines:
        first = fc["casts"][0]
        w["season"] = "10月初初秋（高德实况预报）"
        try:
            w["high"] = max(int(c["daytemp"]) for c in fc["casts"])
            w["low"] = min(int(c["nighttemp"]) for c in fc["casts"])
        except Exception:
            pass
    return "天气已回填: " + "；".join(lines)


def main():
    if not KEY:
        print("缺少 AMAP_WEB_KEY 环境变量"); sys.exit(1)
    path = sys.argv[1]
    trip = json.load(open(path, encoding="utf-8"))
    for grp in ("pois", "hotels", "restaurants"):
        for obj in trip.get(grp, []):
            print(f"[{grp}] {obj['id']} {obj['name']}: {fill_one(obj)}")
    print("weather:", fill_weather(trip))
    trip["_geoFilled"] = True
    with open(path, "w", encoding="utf-8") as f:
        json.dump(trip, f, ensure_ascii=False, indent=1)
    print("已写回", path)


if __name__ == "__main__":
    main()
