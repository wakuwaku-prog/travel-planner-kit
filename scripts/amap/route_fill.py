#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""用高德 direction API 为每日行程填充真实路线(距离/耗时/tojump坐标)。
避免调用次数过多:逐行串起 daily 内已选且勾选(checked)的 poi,切分双点 driving。
"""
import json, os, sys, time, urllib.parse, urllib.request

KEY = os.environ.get("AMAP_WEB_KEY", "")
BASE = "https://restapi.amap.com/v3/direction/driving"


def geo_iter(path):
    """逐行产出一个 poi。"""
    for p in path:
        yield p


def call_driving(origin, dest):
    params = {"origin": origin, "destination": dest, "strategy": 0, "extensions": "base", "key": KEY}
    url = BASE + "?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(url, timeout=20) as r:
        return json.load(r)


def fill_trip(trip, out_path):
    by_id = {p["id"]: p for p in trip["pois"]}
    by_id.update({p["id"]: p for p in trip.get("restaurants", [])})
    by_id.update({p["id"]: p for p in trip.get("hotels", [])})
    finished = []
    for day in trip.get("itinerary", []):
        seq = []
        # 按 items 顺序,提取坐标
        for it in day.get("items", []):
            pid = it.get("poiId")
            p = by_id.get(pid)
            if p and ("lat" in p and p["lat"]):
                seq.append(p)
        # 双点 route 计算
        route = day.setdefault("dailyRoute", {})
        legs = []
        total_d = 0.0
        total_t = 0
        for i in range(len(seq) - 1):
            a, b = seq[i], seq[i + 1]
            o = f"{float(a['lng']):.6f},{float(a['lat']):.6f}"
            d = f"{float(b['lng']):.6f},{float(b['lat']):.6f}"
            try:
                res = call_driving(o, d)
                if res.get("status") == "1":
                    path = res["route"]["paths"][0]
                    dist = float(path.get("distance", 0))
                    durt = int(path.get("duration", 0))
                    total_d += dist
                    total_t += durt
                    legs.append({"from": a["id"], "to": b["id"], "distanceKm": round(dist / 1000, 2), "durationMin": round(durt / 60, 1)})
                else:
                    legs.append({"from": a["id"], "to": b["id"], "error": res.get("info")})
            except Exception as e:
                legs.append({"from": a["id"], "to": b["id"], "error": str(e)})
            time.sleep(0.35)
        route["legs"] = legs
        route["distanceKm"] = round(total_d / 1000, 2)
        route["durationMin"] = round(total_t / 60, 1)
        finished.append({"day": day["day"], "theme": day.get("theme"), "items": len(seq), "route": route})
    trip["_routeFilled"] = True
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(trip, f, ensure_ascii=False, indent=1)
    return finished


if __name__ == "__main__":
    p = sys.argv[1]
    trip = json.load(open(p, encoding="utf-8"))
    res = fill_trip(trip, p)
    for d in res:
        r = d["route"]
        print(f"Day{d['day']} {d['theme']}: legs={len(r.get('legs', []))} dist={r['distanceKm']}km dur={r['durationMin']}min")
