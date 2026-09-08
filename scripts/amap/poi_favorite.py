#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""为行程中每个点位反查高德 POI ID（poiId），供「收藏到高德」功能使用。

原理：官方不支持第三方直接写入个人收藏夹；官方可行路径是 URI API 打开
「地点详情页」(https://uri.amap.com/poidetail?poiid=xx)，用户在详情页点
星形「收藏」按钮手动收藏（需登录高德账号，多端同步）。

本脚本给 pois/hotels/restaurants 里带坐标的点补 poiId：
  1. 已有 poiId 的保留；
  2. 否则用 /v3/place/around 按坐标就近取一个 POI（radius 500m）；
  3. 带名称的点可额外尝试 /v3/place/text 精确匹配（名称字段优先）。
"""
import json, os, sys, time, urllib.parse, urllib.request

KEY = os.environ.get("AMAP_WEB_KEY", "")
BASE = "https://restapi.amap.com/v3"
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def req(path, params):
    params = {"key": KEY, **params}
    url = f"{BASE}{path}?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(url, timeout=20) as r:
        return json.load(r)


def find_poi_id(name, lng, lat):
    # 1) 周边搜索（按坐标取最近 POI）
    try:
        d = req("/place/around", {"location": f"{lng},{lat}", "radius": 500, "offset": 3, "extensions": "base"})
        pois = d.get("pois") or []
        if pois:
            # 优先名称包含匹配，否则取第一个
            for p in pois[:3]:
                if name and (name in p.get("name", "") or p.get("name", "") in name):
                    return p.get("id")
            return pois[0].get("id")
    except Exception:
        pass
    # 2) 关键词精确搜索兜底
    if name:
        try:
            d = req("/place/text", {"keywords": name, "offset": 3, "extensions": "base"})
            for p in (d.get("pois") or [])[:3]:
                if name in p.get("name", "") or p.get("name", "") in name:
                    return p.get("id")
            if d.get("pois"):
                return d["pois"][0].get("id")
        except Exception:
            pass
    return None


def main():
    targets = sys.argv[1:] or [os.path.join(BASE_DIR, "data", "trips", "trip-*.json")]
    for f in targets:
        if "*" in f:
            import glob
            files = sorted(glob.glob(f))
        else:
            files = [f]
        for tf in files:
            trip = json.load(open(tf, encoding="utf-8"))
            done = []
            for group in ("pois", "hotels", "restaurants"):
                for p in trip.get(group, []):
                    if p.get("poiId") or not p.get("lng"):
                        continue
                    pid = find_poi_id(p.get("name", ""), float(p["lng"]), float(p["lat"]))
                    if pid:
                        p["poiId"] = pid
                        done.append((group, p.get("name"), pid))
                    time.sleep(0.25)
            json.dump(trip, open(tf, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
            print(f"{tf}: 回填 poiId {len(done)} 个")
            for g, n, pid in done[:8]:
                print(f"   [{g}] {n} -> {pid}")


if __name__ == "__main__":
    main()