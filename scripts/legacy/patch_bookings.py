#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""补充子代理最新确认的预约规则（钟鼓索道/厦大3天/单买预约）到 trip JSON"""
import json, os

tp = r"C:/Users/epiph/Desktop/DSH工作/travel-site/data/trips/trip-xiamen-2026-09-18.json"
trip = json.load(open(tp, encoding="utf-8"))

if not any(e["id"] == "e11" for e in trip["experiences"]):
    trip["experiences"].append({
        "id": "e11", "name": "钟鼓索道（空中看厦门）", "where": "植物园西门旁（万石植物园站）",
        "durationMin": 60, "price": "约65-70元/人（示例）", "bookingRequired": True,
        "bookingLink": "官方渠道提前预约", "bestFor": "想俯瞰厦门全景的人", "sourceIds": ["v03"],
    })

bks = {b["item"] for b in trip["tips"]["bookings"]}
adds = [
    {"item": "钟鼓索道", "how": "提前7天抢票（8点放票）", "deadline": "提前7天"},
    {"item": "鼓浪屿收费景点（日光岩/菽庄等）", "how": "单买需预约、联票免预约（子代理核实）", "deadline": "当天"},
]
for a in adds:
    if a["item"] not in bks:
        trip["tips"]["bookings"].append(a)
        bks.add(a["item"])

# 厦大预约期限修正
for b in trip["tips"]["bookings"]:
    if b["item"] == "厦门大学" and "3天" not in b.get("deadline", ""):
        b["deadline"] = "提前3天（含周末）"

trip["meta"]["status"] = "调研完成：16视频(5全量转写)+79小红书；预约规则已按子代理核实更新"
json.dump(trip, open(tp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("预约清单:", len(trip["tips"]["bookings"]), "| 体验:", len(trip["experiences"]))