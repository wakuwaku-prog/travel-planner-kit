#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""重构 trip JSON：按 B站视频验证的行程结构（D1 老城+集美 / D2 山海环岛 / D3 鼓浪屿全日）"""
import json, os

base = r"C:/Users/epiph/Desktop/DSH工作/travel-site"
tp = os.path.join(base, "data/trips/trip-xiamen-2026-09-18.json")
trip = json.load(open(tp, encoding="utf-8"))
p2 = {o["name"]: o for o in json.load(open(os.path.join(base, "data/research/xiamen_pois2_raw.json"), encoding="utf-8")) if o.get("status") == "1"}

def g(n):
    o = p2.get(n) or {}
    return float(o.get("lng") or 0), float(o.get("lat") or 0)

pois = [
 {"id":"p01","category":"景点","name":"鼓浪屿（全岛）","address":"厦门市思明区鼓浪屿","lng":118.066102,"lat":24.446214,"day":3,"slot":"全日","durationMin":600,"bookingRequired":True,"bookingNote":"东渡邮轮码头→三丘田/内厝澳，船票提前10天放票","ticketPrice":"船票35元(普通)/80元(豪华)，回程免费","openHours":"轮渡 7:00-18:30 左右","tags":["世界遗产","万国建筑","琴岛"],"notes":"主码头东渡；船票小程序购；不要信路边拉客","sourceIds":["v01","v03"],"checked":True},
 {"id":"p16","category":"景点","name":"日光岩","address":"鼓浪屿","lng":117.0,"lat":24.0,"day":3,"slot":"上午","durationMin":90,"bookingRequired":False,"ticketPrice":"单买50元/联票含","openHours":"8:00-17:30","tags":["登顶","俯瞰全岛"],"notes":"节假日排队严重，建议早去或傍晚","sourceIds":["v01","v03"],"checked":True},
 {"id":"p17","category":"景点","name":"菽庄花园+钢琴博物馆","address":"鼓浪屿","lng":117.0,"lat":24.0,"day":3,"slot":"上午","durationMin":120,"bookingRequired":False,"ticketPrice":"单买30元/联票含","openHours":"8:00-17:30","tags":["园林","钢琴"],"notes":"钢琴博物馆有免费演奏，卡好时间","sourceIds":["v01","v03"],"checked":True},
 {"id":"p18","category":"景点","name":"八卦楼（风琴博物馆）","address":"鼓浪屿","lng":117.0,"lat":24.0,"day":3,"slot":"下午","durationMin":90,"bookingRequired":True,"bookingNote":"需在鼓浪屿核心景点小程序预约场次","ticketPrice":"联票含/单约免费","openHours":"8:30-17:30","tags":["管风琴","红顶"],"notes":"每天有管风琴演奏；有免费讲解","sourceIds":["v01","v03"],"checked":True},
 {"id":"p20","category":"海边","name":"大德记沙滩+皓月园","address":"鼓浪屿东南","lng":117.0,"lat":24.0,"day":3,"slot":"傍晚","durationMin":120,"bookingRequired":False,"ticketPrice":"免费(皓月园门票另计)","openHours":"全天","tags":["日落","郑成功像","双子塔同框"],"notes":"退潮礁石注意防滑","sourceIds":["v01","v03"],"checked":True},
 {"id":"p02","category":"街区","name":"中山路步行街","address":"厦门市思明区中山路","lng":118.081903,"lat":24.454104,"day":1,"slot":"上午","durationMin":120,"bookingRequired":False,"ticketPrice":"免费","openHours":"全天","tags":["骑楼","步行街"],"notes":"老虎城四楼天台可拍全景(10元)；中华城免费","sourceIds":["v01","v03"],"checked":True},
 {"id":"p11","category":"市集","name":"厦门八市（营平菜市场）","address":"厦门市思明区营平路","lng":118.075017,"lat":24.457902,"day":1,"slot":"上午","durationMin":90,"bookingRequired":False,"ticketPrice":"免费","openHours":"全天","tags":["水产市场","小吃"],"notes":"看热闹为主，海鲜加工慎重；阿杰五香等小吃在此","sourceIds":["v01","v03"],"checked":True},
 {"id":"p08","category":"景区","name":"集美学村","address":"厦门市集美区","lng":118.103353,"lat":24.572373,"day":1,"slot":"下午","durationMin":240,"bookingRequired":False,"ticketPrice":"免费","openHours":"全天","tags":["嘉庚建筑","海上地铁"],"notes":"地铁1号线直达；龙舟池/鳌园/嘉庚故居/大社戏台","sourceIds":["v01","v03"],"checked":True},
 {"id":"p15","category":"观景","name":"十里长堤（集美）","address":"厦门市集美区","lng":118.089475,"lat":24.563722,"day":1,"slot":"傍晚","durationMin":120,"bookingRequired":False,"ticketPrice":"免费","openHours":"全天","tags":["日落","夜市","乐队"],"notes":"地铁穿海+日落+不定期免费演出","sourceIds":["v01","xhs_695b6c51000000001a02654d"],"checked":True},
 {"id":"p04","category":"景点","name":"厦门园林植物园","address":"厦门市思明区虎园路","lng":118.109277,"lat":24.447728,"day":2,"slot":"上午","durationMin":180,"bookingRequired":False,"ticketPrice":"约30元","openHours":"6:30-18:00","tags":["雨林世界","多肉"],"notes":"西门进+观光车；雨林喷雾8:00-9:30/15:00-16:30","sourceIds":["v01","v03"],"checked":True},
 {"id":"p05","category":"人文","name":"南普陀寺","address":"厦门市思明区思明南路","lng":118.095336,"lat":24.440836,"day":2,"slot":"上午","durationMin":90,"bookingRequired":True,"bookingNote":"访客需预约","ticketPrice":"免费","openHours":"8:00-17:00","tags":["闽南佛教","素饼"],"notes":"东门进长津阁石阶20分钟到免费观景台；西门出接猫街","sourceIds":["v01","v03"],"checked":True},
 {"id":"p14","category":"街区","name":"顶澳仔猫街","address":"厦门市思明区顶澳仔路","lng":118.091662,"lat":24.440171,"day":2,"slot":"上午","durationMin":60,"bookingRequired":False,"ticketPrice":"免费","openHours":"全天","tags":["猫咪涂鸦","拍照"],"notes":"无真猫，涂鸦打卡地","sourceIds":["v03"],"checked":True},
 {"id":"p03","category":"街区","name":"沙坡尾艺术西区","address":"厦门市思明区大学路","lng":118.087587,"lat":24.437609,"day":2,"slot":"中午","durationMin":120,"bookingRequired":False,"ticketPrice":"免费","openHours":"全天","tags":["文艺","老渔港"],"notes":"彩虹墙在艺术西区2楼天台；拍照为主","sourceIds":["v01","v03"],"checked":True},
 {"id":"p06","category":"海滩","name":"白城沙滩","address":"厦门市思明区环岛南路","lng":118.100875,"lat":24.432281,"day":2,"slot":"下午","durationMin":90,"bookingRequired":False,"ticketPrice":"免费","openHours":"全天","tags":["沙滩","日落"],"notes":"日落分神级；人较多","sourceIds":["v01","v03"],"checked":True},
 {"id":"p13","category":"桥梁","name":"演武大桥观景台","address":"厦门市思明区环岛南路","lng":118.087789,"lat":24.435421,"day":2,"slot":"下午","durationMin":60,"bookingRequired":False,"ticketPrice":"免费","openHours":"全天","tags":["海景","双子塔机位"],"notes":"拍世茂双子塔经典机位","sourceIds":["v03"],"checked":True},
 {"id":"p07","category":"道路","name":"环岛路（白城→黄厝）","address":"厦门市思明区环岛路","lng":118.142325,"lat":24.431453,"day":2,"slot":"下午","durationMin":180,"bookingRequired":False,"ticketPrice":"免费","openHours":"全天","tags":["骑行","海景"],"notes":"可29路公交1元走全程；黄厝日出/日落均可","sourceIds":["v01","v03"],"checked":True},
 {"id":"p10","category":"海滩","name":"黄厝海滩","address":"厦门市思明区环岛南路","lng":118.228083,"lat":24.64782,"day":2,"slot":"傍晚","durationMin":90,"bookingRequired":False,"ticketPrice":"免费","openHours":"全天","tags":["日落","人少"],"notes":"看日落最佳；附近海边咖啡馆多","sourceIds":["v01","v04"],"checked":True},
 {"id":"p12","category":"公园","name":"厦门铁路文化公园","address":"厦门市思明区","lng":118.102223,"lat":24.460383,"day":2,"slot":"机动","durationMin":90,"bookingRequired":False,"ticketPrice":"免费","openHours":"全天","tags":["老铁路","免费"],"notes":"可选：大生里段穿鸿山隧道；时间紧可跳过","sourceIds":["v01"],"checked":False},
 {"id":"p21","category":"交通","name":"东渡邮轮码头","address":"厦门市思明区东渡路","lng":118.077007,"lat":24.49397,"day":3,"slot":"07:30出发","durationMin":60,"bookingRequired":True,"bookingNote":"去鼓浪屿主码头上船点","ticketPrice":"—","openHours":"随班次","tags":["船票","码头"],"notes":"提前到码头取票/刷码","sourceIds":["v03"],"checked":True},
]
fix = {"p16": p2.get("日光岩", {}), "p17": p2.get("菽庄花园", {}), "p18": p2.get("八卦楼", {}), "p20": p2.get("皓月园", {})}
for p in pois:
    if p["id"] in fix and fix[p["id"]].get("lng"):
        p["lng"] = fix[p["id"]]["lng"]
        p["lat"] = fix[p["id"]]["lat"]
trip["pois"] = pois

it = [
 {"day": 1, "date": "2026-09-18", "theme": "老城烟火+集美学村（1号线沿线）", "area": "中山路/八市/集美",
  "items": [{"poiId": "p02", "time": "09:00-11:00"}, {"poiId": "p11", "time": "11:00-12:30"}, {"poiId": "r01", "time": "12:30-13:30"}, {"poiId": "p08", "time": "14:00-17:30"}, {"poiId": "p15", "time": "17:30-19:00"}],
  "dailyRoute": {"mode": "地铁1号线+步行", "polylines": [], "distanceKm": 0, "durationMin": 0, "note": "1号线串联：中山路→集美学村"}, "notes": "八市看热闹别乱买海鲜；集美学村值得慢逛"},
 {"day": 2, "date": "2026-09-19", "theme": "山海环岛：植物园→厦大→环岛路", "area": "思明东南",
  "items": [{"poiId": "p04", "time": "08:30-11:30"}, {"poiId": "p05", "time": "11:30-13:00"}, {"poiId": "p14", "time": "13:00-13:40"}, {"poiId": "p03", "time": "13:40-14:40"}, {"poiId": "p06", "time": "15:00-16:00"}, {"poiId": "p13", "time": "16:00-17:00"}, {"poiId": "p07", "time": "17:00-18:30"}, {"poiId": "p10", "time": "18:30-19:30"}],
  "dailyRoute": {"mode": "driving", "polylines": [], "distanceKm": 0, "durationMin": 0, "note": "可29路公交串联"}, "notes": "植物园西门进；南普陀需预约；沙坡尾拍照打卡"},
 {"day": 3, "date": "2026-09-20", "theme": "鼓浪屿全日：码头→三大片区", "area": "鼓浪屿",
  "items": [{"poiId": "p21", "time": "07:30-08:30"}, {"poiId": "p16", "time": "09:30-11:00"}, {"poiId": "p17", "time": "11:00-12:30"}, {"poiId": "p01", "time": "12:30-13:30", "label": "龙头路小吃街午餐"}, {"poiId": "p18", "time": "13:30-15:00"}, {"poiId": "p20", "time": "16:00-17:30"}],
  "dailyRoute": {"mode": "步行", "polylines": [], "distanceKm": 0, "durationMin": 0, "note": "岛上不通车"}, "notes": "船票提前10天买；日光岩早去；八卦楼需预约场次"},
]
trip["itinerary"] = it

trip["experiences"].extend([
 {"id": "e07", "name": "帆船出海", "where": "五缘湾帆船港", "durationMin": 90, "price": "约120-200元/人（示例）", "bookingRequired": True, "bookingLink": "平台购票", "bestFor": "喜欢海的朋友", "sourceIds": ["v03"]},
 {"id": "e08", "name": "赶海挖沙", "where": "观音山沙滩", "durationMin": 120, "price": "免费（查好潮汐表）", "bookingRequired": False, "bestFor": "亲子", "sourceIds": ["v03"]},
 {"id": "e09", "name": "山海健康步道临海线", "where": "第18出入口→盼归塔（速通：云山天际酒店旁24口电梯）", "durationMin": 150, "price": "免费", "bookingRequired": False, "bestFor": "徒步爱好者", "sourceIds": ["v03"]},
 {"id": "e10", "name": "集美海上自行车道", "where": "集美学村·海上自行车道（2.6km）", "durationMin": 30, "price": "骑行约10-20元", "bookingRequired": False, "bestFor": "骑行", "sourceIds": ["v03"]},
])
trip["tips"]["bookings"].extend([
 {"item": "鼓浪屿船票", "how": "微信小程序（提前10天放票，节假日必须提前）；普通35元/豪华80元，回程免费", "deadline": "提前10天"},
 {"item": "厦门大学", "how": "南门访客中心预约（群贤楼群→芙蓉隧道路线）", "deadline": "提前1-3天"},
 {"item": "日光岩/菽庄/八卦楼", "how": "可单独购票或买联票更划算；八卦楼需预约场次", "deadline": "当天"},
])
trip["tips"]["transportSchedules"] = [
 {"line": "机场→市区", "note": "公交机场专线1元/机场巴士；或BRT全程高架无红绿灯，超快"},
 {"line": "厦门北站→岛内", "note": "地铁1号线直达，转集美学村同线"},
 {"line": "环岛路海岸线", "note": "29路公交1元，完整走完海岸线"},
 {"line": "上海→厦门", "note": "高铁约5-6h / 飞机约2h（示例，请查询实时）"},
]
trip["meta"]["status"] = "调研完成：16视频+79小红书，B站要点已合并(3/5)，行程按视频验证重构"
json.dump(trip, open(tp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("行程重构完成 | POIs:", len(trip["pois"]), "| 体验:", len(trip["experiences"]), "| 预约:", len(trip["tips"]["bookings"]))