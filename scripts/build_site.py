#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""将 data/trips/trip-*.json 渲染成单文件/travel-site/site/index.html
带高德 JS API 每日路线 + 一键高德导航。部署静态站即可用。
"""
import json, os, glob, sys, urllib.parse

SITE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "site")
TRIP_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "trips")
AMAP_JKEY = os.environ.get("AMAP_JS_KEY", "2525e1aeef193f334882762b43b3b7ba")


def route_url(mode="car"):
    return f"https://uri.amap.com/navigation?to={{to}}&mode={mode}&callnative=1"


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def poi_card(p, nav_base):
    checked = "checked" if p.get("checked", True) else ""
    srcs = "<br>".join([f"<a href='{s['url']}'>{s['title'][:28]}</a>" for s in p.get("sources", [])])
    tags = " ".join(f"<span class='tag'>{esc(t)}</span>" for t in p.get("tags", []))
    return f"""
    <article class='poi' id='poi-{p['id']}' data-lng='{p.get('lng','')}' data-lat='{p.get('lat','')}'>
      <label class='check'><input type='checkbox' {checked} data-id='{p['id']}'> 加入当日行程</label>
      <h3>{esc(p['name'])} <span class='src'>{esc(p.get('address',''))}</span></h3>
      <div class='meta'>{" · ".join([x for x in [p.get('openHours'),p.get('ticketPrice','免费'), " / ".join(p.get('tags', [])) if isinstance(p.get('tags', []), list) else p.get('tags','')] if x])}</div>
      <p>{esc(p.get('notes',''))}</p>
      {tags}
      <div class='actions'>
        <a class='nav' href='{nav_base.format(to=f"{p['lng']},{p['lat']},{urllib.parse.quote(p['name'])}")}' target='_blank'>🧭 高德导航</a>
        <a class='detail' target='_blank' data-poi='{p['id']}' href='javascript:;'>详情</a>
      </div>
      <div class='sources'>{srcs}</div>
    </article>"""


def render(itinerary_by_day, pois_by_id, by_cat):
    html = HTML_TEMPLATE
    nav = route_url
    # 逐日详情 + 地图初始化数据
    day_blocks = []
    map_days = {}
    for day in itinerary_by_day.values():
        items = day.get("items", [])
        blocks = []
        pts = []
        for it in items:
            pid = it.get("poiId")
            p = pois_by_id.get(pid)
            if not p:
                continue
            blocks.append(f"<li><b>{esc(it.get('time',''))}</b> {esc(p['name'])}<a class='nav-mini' href='{nav.format(to=f"{p['lng']},{p['lat']},{urllib.parse.quote(p['name'])}")}'>导航</a></li>")
            if p.get("lat"):
                pts.append({"lng": p["lng"], "lat": p["lat"], "name": p["name"], "id": pid})
        map_days[day["day"]] = pts
        day_blocks.append(f"""
        <section class='daycard' id='day-{day['day']}' data-day='{day['day']}'>
          <h2>DAY {day['day']} · {esc(day['date'])} <span class='theme'>{esc(day.get('theme',''))}</span></h2>
          <ol class='poilist'>{''.join(blocks)}</ol>
          <p class='routeinfo'>{esc(' · '.join([str(x) for x in [f"{day.get('dailyRoute',{}).get('distanceKm')} km", f"{day.get('dailyRoute',{}).get('durationMin')} min", day.get('dailyRoute',{}).get('mode')] if x]))})</p>
          <p class='notes'>{esc(day.get('notes',''))}</p>
        </section>""")
    # 栏目列表
    catblocks = {}
    for cat in ("pois", "hotels", "restaurants", "experiences"):
        objs = by_cat.get(cat, [])
        catblocks[cat] = objs
    html = html.replace("__DAYCARDS__", "\n".join(day_blocks))
    html = html.replace("__MAPDAYS__", "null" if not map_days else ",\n".join(f"[{day}]:{pts}" for day, pts in map_days.items()) if False else json.dumps(map_days))
    # TODO 简化:POIs / 其它栏目后续填; 先把卡片集中放在一个 containers
    html = html.replace("__POIHTML__", "\n".join(poi_card(p, route_url()) for cat in ("pois", ) for p in catblocks.get(cat, [])))
    return html


HTML_TEMPLATE = """<!doctype html>
<html lang='zh-CN'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>
<title>__TITLE__ 旅行攻略</title><style>
:root{--main:#0a6cff;--orange:#ff7a18;--bg:#f7f9fc;--card:#fff}
*{box-sizing:border-box}body{margin:0;font-family:-apple-system,'PingFang SC','Microsoft YaHei',sans-serif;background:var(--bg);color:#1c2733}
header{padding:18px 22px;background:linear-gradient(135deg,#0a6cff,#00a6e6 60%,#72e0c7);color:#fff}
header h1{margin:0;font-size:22px}header .sub{opacity:.92;margin-top:6px;font-size:13px}
.container{max-width:1180px;margin:0 auto;padding:18px}.topbar{display:flex;gap:8px;flex-wrap:wrap;margin:10px 0 18px}
.pill{padding:8px 14px;border:1px solid #dbe3ee;background:var(--card);border-radius:999px;cursor:pointer;font-size:14px}
.pill.on{background:var(--main);color:#fff;border-color:var(--main)}
.grid{display:grid;grid-template-columns:2fr 1fr;gap:18px}@media(max-width:900px){.grid{grid-template-columns:1fr}}
.card{background:var(--card);border:1px solid #e6edf5;border-radius:12px;padding:16px;margin-bottom:16px}
.daycard h2{font-size:17px;margin:0 0 10px}.daycard .theme{color:var(--orange);font-weight:400}
ol.poilist{margin:0;padding-left:0;list-style:none}.poilist li{padding:7px 0;border-bottom:1px dashed #eef3f8;display:flex;align-items:center;gap:8px;justify-content:space-between}
.poilist b{color:var(--main);white-space:nowrap}
.nav-mini{font-size:11px;color:var(--main);text-decoration:none;border:1px solid #cfe0ff;padding:1px 6px;border-radius:6px}
.actions .nav{display:inline-block;margin-top:6px;text-decoration:none;background:var(--main);color:#fff;padding:5px 12px;border-radius:8px;font-size:13px}
.poi{border:1px solid #e6edf5;border-radius:12px;background:var(--card);padding:12px;margin-bottom:12px}
.poi h3{margin:0 0 6px;font-size:16px}.poi .src{font-size:12px;color:#7b8897;font-weight:400}
.poi .meta{color:#5b6b7c;font-size:13px}.tag{display:inline-block;background:#eef4ff;color:#3a6fc4;font-size:12px;padding:2px 8px;border-radius:6px;margin:3px 4px 3px 0}
#mapwrap{height:52vh;border-radius:12px;overflow:hidden;position:sticky;top:8px}
.panel{display:none}.panel.active{display:block}.note{font-size:12px;color:#8895a5;line-height:1.7}
.sources a{font-size:12px;color:#0a6cff;text-decoration:none;display:inline-block;margin:1px 0}
/* 地图编号点 + 地名标注 */
.seqmarker{width:28px;height:28px;border-radius:50%;background:#0a6cff;color:#fff;font-size:13px;font-weight:700;text-align:center;line-height:28px;box-shadow:0 0 0 2px #fff,0 2px 6px rgba(0,0,0,.2)}
.poilabel{font-size:12px;background:rgba(255,255,255,.92);border:1px solid #dbe3ee;border-radius:6px;padding:1px 6px;color:#1c2733;white-space:nowrap}
.hotelmark{width:28px;height:28px;border-radius:50%;background:#b06ae0;color:#fff;font-size:15px;text-align:center;line-height:28px;box-shadow:0 0 0 2px #fff,0 2px 6px rgba(0,0,0,.2)}
/* 顺序导航底部栏 */
#navbar{position:sticky;bottom:0;left:0;right:0;z-index:50;background:#fff;border-top:1px solid #e6edf5;padding:8px 12px;gap:8px;flex-direction:column;box-shadow:0 -3px 12px rgba(0,0,0,.06)}
#navbar .navhead{font-weight:700;font-size:14px}
#navbar .navtip{font-weight:400;color:#8895a5;font-size:11px}
#navbar .chips{display:flex;gap:6px;flex-wrap:wrap}
#navbar .chip{font-size:12px;padding:5px 9px;border-radius:999px;border:1px solid #dbe3ee;background:#f7f9fc;cursor:pointer}
#navbar .chip.cur{background:#0a6cff;color:#fff;border-color:#0a6cff}
#navbar .navctl{display:flex;gap:8px;align-items:center}
#navbar .navctl button{font-size:13px;padding:6px 12px;border-radius:8px;border:1px solid #cfe0ff;background:#eef4ff;color:#0a6cff;cursor:pointer}
/* 手机端：地图置顶吸顶，方便边看边点导航 */
@media(max-width:900px){#mapwrap{order:-1;position:sticky;top:0;z-index:40;height:42vh}}
</style></head><body>
<header><h1>__TITLE__ 之旅 · 3天行程</h1>
<div class='sub'>__SUBTITLE__</div></header>
<div class='container'>
  <div class='topbar'>
    <button class='pill on' data-panel='trip'>📅 行程</button>
    <button class='pill' data-panel='spots'>📍 景点指南</button>
    <button class='pill' data-panel='food'>🍜 餐饮指南</button>
    <button class='pill' data-panel='stays'>🏨 住宿推荐</button>
    <button class='pill' data-panel='exp'>🎨 特色体验</button>
    <button class='pill' data-panel='prep'>🎒 出发前准备</button>
    <button class='pill' data-panel='tips'>⚠️ 旅行提醒</button>
    <button class='pill' data-panel='srcs'>📚 资料来源</button>
    <button class='pill' data-panel='import'>📦 导入路线</button>
  </div>
  <div class='grid'>
    <div>
      <div id='panel-trip' class='panel active'>__DAYCARDS__
        <div class='card note'>点击景点卡片勾选/取消 → 地图实时重算今日路线。</div>
      </div>
      <div id='panel-spots' class='panel'><h2>📍 景点指南</h2>__POIHTML__</div>
      <div id='panel-food' class='panel'><h2>🍜 餐饮指南</h2><div class='note'>__FOOD_PLACEHOLDER__</div></div>
      <div id='panel-stays' class='panel'><h2>🏨 推荐住宿位置</h2>__HOTEL_PLACEHOLDER__</div>
      <div id='panel-exp' class='panel'><h2>🎨 当地特色体验</h2>__EXP_PLACEHOLDER__</div>
      <div id='panel-prep' class='panel'><h2>🎒 出发前准备</h2><div class='note'>__PREP_PLACEHOLDER__</div></div>
      <div id='panel-tips' class='panel'><h2>⚠️ 旅行提醒</h2><div class='note'>__TIPS_PLACEHOLDER__</div></div>
      <div id='panel-srcs' class='panel'><h2>📚 资料来源（__SRC_COUNT__ 条）</h2>__SRC_PLACEHOLDER__</div>
      <div id='panel-import' class='panel'><h2>📦 把行程导入高德地图 / 旅行软件</h2>__IMPORT_PLACEHOLDER__</div>
    </div>
    <div><div id='mapwrap'><div id='map'></div></div></div>
  </div>
</div>
<script src='https://webapi.amap.com/maps?v=2.0&key=__AMAPKEY__&plugin=AMap.Driving,AMap.Walking,AMap.Transfer'></script>
<script>
window.__DAYS__ = __MAPDAYS__;
window.__HOTELS__ = __HOTELS_JSON__;
// 给每天的点编号
(function(){ for(var d in window.__DAYS__){ var arr=window.__DAYS__[d]; arr.forEach(function(p,i){ p.seq=i+1; }); } })();
var mp = new AMap.Map('map',{zoom:11,center:[118.09,24.47]});
var routeLayers=[], markerLayers=[], activeDay=1;
function navUrl(p){ return 'https://uri.amap.com/navigation?to='+p.lng+','+p.lat+','+encodeURIComponent(p.name)+'&mode=car&callnative=1'; }
function clearLayers(){ routeLayers.concat(markerLayers).forEach(function(l){l.setMap&&l.setMap(null)}); routeLayers=[]; markerLayers=[]; }
function drawDay(d){
  clearLayers();
  var pts=(window.__DAYS__[d]||[]).filter(function(p){return p&&p.lat});
  if(pts.length<2) return;
  var path=pts.map(function(p){return [p.lng,p.lat]});
  var poly=new AMap.Polyline({path:path,strokeColor:'#0a6cff',strokeWeight:6,strokeOpacity:.9,lineJoin:'round',borderWeight:2,strokeStyle:'solid'});
  poly.setMap(mp); routeLayers.push(poly);
  // 编号+地名标注
  pts.forEach(function(p){
    var m=new AMap.Marker({
      position:[p.lng,p.lat], zIndex:120,
      content:'<div class="seqmarker" data-name="'+p.name+'">'+p.seq+'</div>',
      offset:new AMap.Pixel(-14,-14)
    });
    m.setMap(mp); markerLayers.push(m);
    // 名称 label
    var lb=new AMap.Text({position:[p.lng,p.lat],content:'<div class="poilabel">'+(p.seq+'. '+p.name)+'</div>',offset:new AMap.Pixel(0,12),zIndex:130});
    lb.setMap(mp); markerLayers.push(lb);
  });
  mp.setFitView([poly]);
  renderNavbar(d, pts);
}
function renderNavbar(d, pts){
  var bar=document.getElementById('navbar'); if(!bar) return;
  var html='<div class="navhead">Day'+d+' 顺序导航 <span class="navtip">点站点直开高德</span></div>';
  html+='<div class="chips">';
  pts.forEach(function(p,i){ html+='<button class="chip" data-i="'+i+'">'+p.seq+'. '+p.name+'</button>'; });
  html+='</div><div class="navctl"><button id="prevStop">⬅ 上一站</button><button id="nextStop">下一站 ➡</button></div>';
  bar.innerHTML=html;
  var chips=bar.querySelectorAll('.chip');
  chips.forEach(function(c){ c.addEventListener('click',function(){ window.open(navUrl(pts[+c.dataset.i]),'_blank'); }); });
  var cur=0;
  function hi(i){ cur=i; chips.forEach(function(c,j){ c.classList.toggle('cur', j===i); }); }
  hi(0);
  bar.querySelector('#prevStop').addEventListener('click',function(){ if(cur>0) hi(cur-1); });
  bar.querySelector('#nextStop').addEventListener('click',function(){ if(cur<pts.length-1){ hi(cur+1); } window.open(navUrl(pts[cur]),'_blank'); });
}
var dayCards=document.querySelectorAll('.daycard');
dayCards.forEach(function(c){c.addEventListener('click',function(){activeDay=+c.dataset.day;drawDay(activeDay);});});
drawDay(1);
// 常显推荐住宿位置（紫色标记，不随每日路线清除）
var hotelLayer=[];
(window.__HOTELS__||[]).forEach(function(h){
  if(!h.lat) return;
  var m=new AMap.Marker({position:[h.lng,h.lat],zIndex:110,content:'<div class="hotelmark">🏨</div>',offset:new AMap.Pixel(-14,-14)});
  m.setMap(mp); hotelLayer.push(m);
  var lb=new AMap.Text({position:[h.lng,h.lat],content:'<div class="poilabel" style="border-color:#e0b0ff;background:#faf0ff">🏨 '+h.name+'</div>',offset:new AMap.Pixel(0,14),zIndex:115});
  lb.setMap(mp); hotelLayer.push(lb);
  var _h=(function(hn){ return function(){ window.open('https://uri.amap.com/navigation?to='+h.lng+','+h.lat+','+encodeURIComponent(hn)+'&mode=car&callnative=1','_blank'); }; })(h.name);
  m.on('click',_h); lb.on('click',_h);
});
var pois=document.querySelectorAll('.poi input[type=checkbox]');
pois.forEach(function(cb){cb.addEventListener('change',function(){ drawDay(activeDay); });});
var btns=document.querySelectorAll('.topbar .pill');
btns.forEach(function(b){b.addEventListener('click',function(){
  btns.forEach(function(x){x.classList.remove('on')});b.classList.add('on');
  document.querySelectorAll('.panel').forEach(function(p){p.classList.remove('active')});
  document.getElementById('panel-'+b.dataset.panel).classList.add('active');
  if(b.dataset.panel==='trip'){ var bar=document.getElementById('navbar'); if(bar) bar.style.display='flex'; }
  else if(b.dataset.panel==='import'){ var nb=document.getElementById('navbar'); if(nb) nb.style.display='none'; }
});});
</script>
<div id='navbar' style='display:flex'></div>
</body></html>
"""


def fill_demo(build=True):
    files = glob.glob(os.path.join(TRIP_DIR, "trip-*.json"))
    if not files:
        # 模板模式：无行程数据时输出说明页
        os.makedirs(SITE_DIR, exist_ok=True)
        html = HTML_TEMPLATE.replace("__AMAPKEY__", AMAP_JKEY) \
            .replace("__TITLE__", "旅行规划模板") \
            .replace("__SUBTITLE__", "还没有行程数据：请让 Agent 按 travel-research 流程生成 data/trips/trip-*.json 后重新运行本脚本") \
            .replace("__DAYCARDS__", "<div class='card note'>没有可显示的行程。⌛ 使用方法见仓库 README：配置高德 Key → Agent 调研 → scripts/amap/route_fill.py → export_routes.py → 本脚本构建。</div>") \
            .replace("__MAPDAYS__", "{}") \
            .replace("__POIHTML__", "<div class='note'>—</div>") \
            .replace("__FOOD_PLACEHOLDER__", "—").replace("__EXP_PLACEHOLDER__", "—") \
            .replace("__HOTEL_PLACEHOLDER__", "—").replace("__HOTELS_JSON__", "[]") \
            .replace("__PREP_PLACEHOLDER__", "—").replace("__TIPS_PLACEHOLDER__", "—") \
            .replace("__SRC_PLACEHOLDER__", "—").replace("__SRC_COUNT__", "0") \
            .replace("__IMPORT_PLACEHOLDER__", "—")
        with open(os.path.join(SITE_DIR, "index.html"), "w", encoding="utf-8") as f:
            f.write(html)
        print("模板模式：无 trip 数据，已生成说明页")
        return
    for f in files:
        trip = json.load(open(f, encoding="utf-8"))
        os.makedirs(SITE_DIR, exist_ok=True)
        title = trip["meta"]["destination"]
        subtitles = f"{title} · {trip['meta']['days']}天 · 出发{trip['meta']['departureCity']} · {trip['meta']['travelers']} · {'/'.join(trip['meta']['preferences'])}"
        by_id = {p["id"]: p for p in trip["pois"]}
        by_id.update({p["id"]: p for p in trip.get("restaurants", [])})
        by_id.update({p["id"]: p for p in trip.get("hotels", [])})
        itinerary = {int(d["day"]): d for d in trip["itinerary"]}
        # 把 source 挂到 pois
        srcmap = {s["id"]: s for s in trip.get("sources", [])}
        for p in trip["pois"]:
            p["sources"] = [srcmap[sid] for sid in p.get("sourceIds", []) if sid in srcmap]
        # 各栏目内容的占位
        prep_html = "\n".join(f"• <b>{esc(b['item'])}</b>：{esc(b['how'])}（{esc(b['deadline'])}）" for b in trip["tips"]["bookings"])
        ts_html = "\n".join(f"• {esc(t['line'])} — {esc(t['note'])}" for t in trip["tips"]["transportSchedules"])
        tips_html = "<h3>天气与打包</h3>· " + esc(trip["tips"]["weather"]["advice"]) + "<br>" + " / ".join(esc(x) for x in trip["tips"]["packing"]) + "<h3>需预约</h3>" + prep_html + "<h3>本地交通</h3>" + ts_html + "<h3>安全/风俗</h3>" + "<br>".join("· "+esc(x) for x in trip["tips"]["safety"]+trip["tips"]["customs"])
        food_html = " / ".join(f"{esc(r['name'])}（{esc(r['type'])}，约¥{r['avgPrice']}）" for r in trip["restaurants"])
        r_html = "\n".join(poi_card({**r, "category": "restaurant", "address": r.get("area", ""), "ticketPrice": f"人均约¥{r.get('avgPrice')}", "openHours": r.get("dianpingKeyword",""), "sources": [srcmap[sid] for sid in r.get("sourceIds", []) if sid in srcmap]}, route_url()) for r in trip["restaurants"])
        exp_html = "\n".join(f"<div class='card'><h3>{esc(e['name'])}</h3><div class='meta'>{esc(e.get('where',''))} · {esc(e.get('durationMin',''))}分钟 · {esc(e.get('price',''))}</div><p>{esc('需预约' if e.get('bookingRequired') else '无需预约')}{' · 预约入口:'+esc(e.get('bookingLink','')) if e.get('bookingLink') else ''} · 适合：{esc(e.get('bestFor',''))}</p></div>" for e in trip["experiences"])
        # 住宿推荐：卡片 + 地图常显数据
        hotel_cards = []
        hotel_pts = []
        for h in trip.get("hotels", []):
            if not h.get("lng"):
                continue
            hotel_pts.append({"name": h["name"], "lng": h["lng"], "lat": h["lat"]})
            badge = " ⭐推荐" if h.get("recommend") else ""
            srcs = "".join(f"<a href='{esc(s.get('url',''))}' target='_blank'>📎 {esc((s.get('title') or s.get('id'))[:30])}</a>" for s in [srcmap.get(sid) for sid in h.get("sourceIds", []) if srcmap.get(sid)])
            nav = f"<a class='nav' href='{route_url().format(to=f"{h['lng']},{h['lat']},{urllib.parse.quote(h['name'])}")}' target='_blank'>🧭 高德导航</a>"
            if h.get("poiId"):
                fav = f"<a class='nav' style='background:#b06ae0' href='https://uri.amap.com/poidetail?poiid={urllib.parse.quote(h['poiId'])}&callnative=1&src=travelsite' target='_blank'>⭐ 收藏</a>"
            else:
                fav = f"<a class='nav' style='background:#b06ae0' href='https://uri.amap.com/marker?position={h['lng']},{h['lat']}&name={urllib.parse.quote(h['name'])}&src=travelsite&coordinate=gaode' target='_blank'>📍 详情</a>"
            hotel_cards.append(f"<article class='poi'><h3>{esc(h['name'])}{badge} <span class='src'>{esc(h.get('area',''))}</span></h3>"
                               f"<div class='meta'>{esc(h.get('priceRange',''))}</div><p>{esc(h.get('notes',''))}</p>"
                               f"<div class='actions'>{nav} {fav}</div><div class='sources'>{srcs}</div></article>")
        hotels_html = "\n".join(hotel_cards) if hotel_cards else "<div class='note'>暂无住宿推荐数据。</div>"
        hotels_json = json.dumps(hotel_pts, ensure_ascii=False)
        html = HTML_TEMPLATE.replace("__AMAPKEY__", AMAP_JKEY).replace("__TITLE__", esc(title)).replace("__SUBTITLE__", esc(subtitles)).replace("__POIHTML__", "\n".join(poi_card(p, route_url()) for p in trip["pois"]))
        # 逐日卡片
        daycards = []
        for d in sorted(itinerary):
            day = itinerary[d]
            blocks = []
            for it in day.get("items", []):
                p = by_id.get(it.get("poiId"))
                if not p:
                    continue
                blocks.append(f"<li><b>{esc(it.get('time',''))}</b> {esc(p['name'])}<a class='nav-mini' href='{route_url().format(to=f"{p['lng']},{p['lat']},{urllib.parse.quote(p['name'])}")}'>导航</a></li>")
            dr = day.get("dailyRoute", {})
            routeinfo = " / ".join([str(x) for x in [f"约{dr.get('distanceKm')} km", f"约{dr.get('durationMin')} min", dr.get('mode')] if x])
            daycards.append(f"""
            <section class='daycard' id='day-{d}' data-day='{d}'>
              <h2>DAY {d} · {esc(day.get('date',''))} <span class='theme'>{esc(day.get('theme',''))}</span></h2>
              <ol class='poilist'>{''.join(blocks)}</ol>
              <p class='routeinfo'>{esc(routeinfo)}</p>
              <p class='notes'>{esc(day.get('notes',''))}</p>
            </section>""")
        html = html.replace("__DAYCARDS__", "\n".join(daycards))
        # 地图数据
        def mkmapdays():
            out = {}
            for d in sorted(itinerary):
                pts = []
                for it in itinerary[d].get("items", []):
                    p = by_id.get(it.get("poiId"))
                    if p and p.get("lat"):
                        pts.append({"id": p["id"], "name": p["name"], "lng": p["lng"], "lat": p["lat"]})
                out[d] = pts
            return out
        html = html.replace("__MAPDAYS__", json.dumps(mkmapdays(), ensure_ascii=False))
        html = html.replace("__POIHTML__", "\n".join(poi_card(p, route_url()) for p in trip["pois"]))
        html = html.replace("__FOOD_PLACEHOLDER__", food_html + "<p style='margin-top:8px'>共 " + str(len(trip["restaurants"])) + " 家候选（坐标来自高德 POI，人均为估算）</p><div style='margin-top:10px'>" + r_html + "</div>")
        html = html.replace("__EXP_PLACEHOLDER__", exp_html)
        html = html.replace("__HOTEL_PLACEHOLDER__", hotels_html)
        html = html.replace("__HOTELS_JSON__", hotels_json)
        html = html.replace("__PREP_PLACEHOLDER__", prep_html + "<h3>本地交通</h3>" + ts_html)
        html = html.replace("__TIPS_PLACEHOLDER__", tips_html)
        # 资料来源面板
        vids = [s for s in trip.get("sources", []) if s.get("type") == "video"]
        posts = [s for s in trip.get("sources", []) if s.get("type") == "post"]
        def src_rows(group):
            return "\n".join(f"<li><a href='{esc(s.get('url',''))}' target='_blank'>{esc((s.get('title') or s.get('id'))[:46])}</a> <span style='color:#8895a5'>{esc(s.get('author',''))} {esc('♥'+str(s.get('likes'))) if s.get('likes') else ''}{esc(' · '+str(s.get('play'))) if s.get('play') else ''}</span></li>" for s in group)
        src_html = f"<h3>B站视频（{len(vids)}）</h3><ol class='poilist'>{src_rows(vids)}</ol><h3>小红书帖子（{len(posts)}）</h3><ol class='poilist'>{src_rows(posts)}</ol>"
        html = html.replace("__SRC_PLACEHOLDER__", src_html).replace("__SRC_COUNT__", str(len(trip.get("sources", []))))
        # 导入路线面板（分日 KML/GPX + 逐段导航 + 说明）
        import_html = []
        EXP = os.path.join(SITE_DIR, "export")
        def files_list(kind):
            rows = []
            if os.path.isdir(EXP):
                for fn in sorted(os.listdir(EXP)):
                    if kind and not fn.endswith(kind): continue
                    if not f.endswith((".kml", ".gpx")): continue
                    size = os.path.getsize(os.path.join(EXP, fn)) // 1024
                    rows.append(f"<a class='nav' style='margin:3px 8px 3px 0' href='export/{fn}' download>⬇️ {fn}（{size}KB）</a>")
            return "".join(rows)
        # 分日 KML/GPX + 总的
        import_html.append("<h3>① 把路线图存进高德（KML 分日 / GPX 通用）</h3>")
        import_html.append("<div style='line-height:1.9'>" + files_list(".kml") + "</div>")
        import_html.append("<div style='line-height:1.9'>" + files_list(".gpx") + "</div>")
        import_html.append("<p style='color:#c00;font-size:12px'><b>重要提醒：</b>高德 App 的『轨迹导入』把文件当<u>运动轨迹</u>解析，<b>只显示一条路线、不显示各景点名称</b>（你在截图中看到的就是这个）。要带地名+编号的线路图，请直接用本站『行程』页的地图（已给每个点加编号与名称，可点站导航）。KML 导入仅适合把整条路线存进『足迹』参考。</p>")
        # 逐段导航（每一段）
        import_html.append("<h3>② 逐段导航（每段一个高德入口）</h3>")
        for d in sorted(itinerary):
            pts = []
            for it in itinerary[d].get("items", []):
                p = by_id.get(it.get("poiId"))
                if p and p.get("lat"):
                    pts.append(p)
            if len(pts) < 2: continue
            import_html.append(f"<div class='card' style='padding:10px'><b>Day{d} · {esc(itinerary[d].get('date',''))}</b>")
            import_html.append("<ol class='poilist' style='font-size:13px'>")
            for i in range(len(pts) - 1):
                a, b = pts[i], pts[i + 1]
                uri = (f"https://uri.amap.com/navigation?from={a['lng']},{a['lat']},{urllib.parse.quote(a['name'])}"
                       f"&to={b['lng']},{b['lat']},{urllib.parse.quote(b['name'])}&mode=car&callnative=1")
                import_html.append(f"<li><b>{i+1}. {esc(a['name'])}</b> → <b>{i+2}. {esc(b['name'])}</b> "
                                   f"<a href='{uri}' target='_blank'>🚗 高德导航</a></li>")
            import_html.append("</ol></div>")
        # 每日整线（起终点）+ QR
        # ③ 收藏到高德（官方可行方式：详情页逐点收藏）
        import_html.append("<h3>③ 📌 把点位收藏进高德（官方方式，逐点确认）</h3>")
        import_html.append("<p style='color:#556;font-size:13px'>高德不允许第三方直接写入收藏夹；官方支持的做法是：点下面的按钮 → 高德打开该地点<b>详情页</b> → 点信息卡的<b>⭐ 收藏</b>按钮（需登录高德账号，收藏会同步到手机）。逐点点完即全部入你的收藏。</p>")
        fav_points = []
        for grp_key in ("pois", "hotels", "restaurants"):
            for p in trip.get(grp_key, []):
                if not p.get("lng"):
                    continue
                nm = p["name"]
                pid = p.get("poiId") or ""
                if pid:
                    uri = f"https://uri.amap.com/poidetail?poiid={urllib.parse.quote(pid)}&callnative=1&src=travelsite"
                    btn = f"<a href='{uri}' target='_blank'>⭐ 收藏：{esc(nm)}</a>"
                else:
                    uri = f"https://uri.amap.com/marker?position={p['lng']},{p['lat']}&name={urllib.parse.quote(nm)}&src=travelsite&coordinate=gaode"
                    btn = f"<a href='{uri}' target='_blank'>📍 查看：{esc(nm)}（无POI_ID，打开标注页）</a>"
                fav_points.append(f"<li>{btn}</li>")
        import_html.append(f"<ol class='poilist' style='font-size:13px'>{''.join(fav_points)}</ol>")
        import_html.append("<p style='color:#8895a5;font-size:12px'>提示：坐标来自高德（GCJ-02）。KML/GPX 供导入轨迹参考；本站地图即最完整的带地名线路图；高德官方不支持第三方静默写入收藏，唯一个人侧官方路径是上面这种『详情页收藏』。</p>")
        html = html.replace("__IMPORT_PLACEHOLDER__", "".join(import_html))
        with open(os.path.join(SITE_DIR, "index.html"), "w", encoding="utf-8") as f:
            f.write(html)
        print("站点已生成:", os.path.join(SITE_DIR, "index.html"))


if __name__ == "__main__":
    fill_demo()
