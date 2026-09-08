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


HTML_TEMPLATE = """
<!doctype html>
<html lang='zh-CN'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>
<title>__TITLE__ 旅行攻略</title>
<style>
/* ===== 设计系统：潮汐 × 闽南砖瓦 ===== */
:root{
  --paper:#f7f9fb;            /* 海雾纸底（偏冷，非奶油） */
  --ink:#12303d;              /* 深海墨蓝 */
  --ink-soft:#4c6472;
  --sea:#0e7490;              /* 主色：潮汐青 */
  --sea-deep:#155e75;
  --dusk:#e5725c;             /* 点缀：落日珊瑚（唯一强调色） */
  --line:#dce7ec;
  --card:#ffffff;
  --glass:rgba(255,255,255,.86);
  --shadow:0 1px 2px rgba(18,48,61,.05),0 8px 24px -12px rgba(18,48,61,.18);
  --radius:16px;
  --font-serif:"Noto Serif SC","Songti SC","STSong","SimSun",serif;
  --font-sans:-apple-system,BlinkMacSystemFont,"PingFang SC","Microsoft YaHei","Segoe UI",sans-serif;
}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;font-family:var(--font-sans);background:var(--paper);color:var(--ink);font-size:15px;line-height:1.6;-webkit-font-smoothing:antialiased}
h1,h2,h3{font-family:var(--font-serif);line-height:1.25;font-weight:700}
a{color:var(--sea)}
:focus-visible{outline:2px solid var(--dusk);outline-offset:2px;border-radius:4px}
@media (prefers-reduced-motion:reduce){*,*::before,*::after{transition:none!important;animation:none!important}}

/* ===== 页头：航线卡片式 hero ===== */
header{position:relative;color:#fff;background:linear-gradient(135deg,#0f4c5c 0%,var(--sea) 55%,#0aa5a0 100%);padding:26px 22px 34px;overflow:hidden}
header::after{content:"";position:absolute;left:0;right:0;bottom:-2px;height:26px;background:var(--paper);border-radius:100% 100% 0 0/100% 100% 0 0}
header .hwrap{max-width:1180px;margin:0 auto;position:relative;z-index:1}
header h1{margin:0;font-size:clamp(24px,4.6vw,34px);letter-spacing:.02em}
header .sub{margin-top:8px;font-size:13.5px;opacity:.9;max-width:70ch}
.metachips{display:flex;flex-wrap:wrap;gap:8px;margin-top:14px}
.metachip{background:rgba(255,255,255,.16);border:1px solid rgba(255,255,255,.28);backdrop-filter:blur(4px);border-radius:999px;padding:4px 12px;font-size:12.5px}
.metachip b{font-weight:600}

/* ===== 栏目导航：吸顶玻璃条 ===== */
.topbar{position:sticky;top:0;z-index:60;display:flex;gap:8px;align-items:center;background:var(--glass);backdrop-filter:blur(10px);border-bottom:1px solid var(--line);padding:10px 14px;margin:0 -14px 18px;box-shadow:0 4px 16px -12px rgba(18,48,61,.2)}
.topbar::-webkit-scrollbar{display:none}
.pill{flex:0 0 auto;border:1px solid var(--line);background:#fff;color:var(--ink-soft);border-radius:999px;padding:8px 15px;font-size:13.5px;cursor:pointer;transition:all .18s ease;font-family:var(--font-sans)}
.pill:hover{border-color:var(--sea);color:var(--sea);transform:translateY(-1px)}
.pill.on{background:var(--sea);border-color:var(--sea);color:#fff;box-shadow:0 6px 16px -8px rgba(14,116,144,.55)}

/* ===== 布局 ===== */
.container{max-width:1180px;margin:0 auto;padding:0 14px 40px}
.grid{display:grid;grid-template-areas:"content map";grid-template-columns:minmax(0,1.7fr) minmax(300px,1fr);gap:20px;align-items:start}
.col-content{grid-area:content;min-width:0}
.col-map{grid-area:map;min-width:0}
.grid.no-map{grid-template-areas:"content";grid-template-columns:minmax(0,1fr)}
.grid.no-map .col-map{display:none}

/* ===== 面板 ===== */
.panel{display:none}
.panel.active{display:block;animation:panelIn .22s ease}
@keyframes panelIn{from{opacity:0;transform:translateY(4px)}to{opacity:1;transform:none}}
.panel>h2{font-size:21px;margin:2px 0 14px;color:var(--ink)}
.panel>h3{font-size:16px;margin:18px 0 8px;color:var(--ink)}
.note{font-size:13px;color:var(--ink-soft);line-height:1.7}

/* ===== 卡片通用 ===== */
.card{background:var(--card);border:1px solid var(--line);border-radius:var(--radius);padding:16px;margin-bottom:16px;box-shadow:var(--shadow)}

/* ===== 每日行程：时间线 ===== */
.daycard{background:var(--card);border:1px solid var(--line);border-radius:var(--radius);padding:18px 18px 10px;margin-bottom:16px;box-shadow:var(--shadow);cursor:pointer;transition:border-color .2s, box-shadow .2s}
.daycard:hover{border-color:var(--sea)}
.daycard.on{border-color:var(--sea);box-shadow:0 12px 28px -14px rgba(14,116,144,.35)}
.dayhead{display:flex;align-items:flex-start;gap:12px}
.daynum{flex:0 0 auto;width:44px;height:44px;border-radius:14px;background:linear-gradient(145deg,var(--sea),var(--sea-deep));color:#fff;font-family:var(--font-serif);font-weight:700;font-size:17px;display:flex;align-items:center;justify-content:center;box-shadow:0 6px 14px -6px rgba(21,94,117,.5)}
.dh-txt{min-width:0}
.dh-txt h2{margin:2px 0 2px;font-size:17px}
.daymeta{font-size:12.5px;color:var(--ink-soft)}
ol.poilist{list-style:none;margin:12px 0 4px;padding:0;position:relative}
ol.poilist li{position:relative;padding:8px 0 8px 26px;border-bottom:1px dashed var(--line)}
ol.poilist li:last-child{border-bottom:none}
ol.poilist li::before{content:"";position:absolute;left:7px;top:16px;width:8px;height:8px;border-radius:50%;background:var(--sea);opacity:.85}
ol.poilist li::after{content:"";position:absolute;left:10px;top:28px;bottom:-6px;width:2px;background:linear-gradient(var(--sea),rgba(14,116,144,.15))}
ol.poilist li:last-child::after{display:none}
ol.poilist b{color:var(--sea);white-space:nowrap;font-size:12.5px;margin-right:8px;font-weight:600}
.nav-mini{flex:0 0 auto;font-size:12px;color:var(--sea);text-decoration:none;border:1px solid #bfdce6;padding:2px 10px;border-radius:999px;margin-left:8px;transition:all .15s}
.nav-mini:hover{background:var(--sea);color:#fff}
.routeinfo{font-size:12.5px;color:var(--ink-soft);background:#eef6f9;border-radius:8px;padding:6px 10px;display:inline-block;margin:6px 0 2px}
.notes{font-size:13px;color:var(--ink-soft);margin:6px 0 10px}

/* ===== POI / 酒店 / 餐厅卡片 ===== */
.poi{background:var(--card);border:1px solid var(--line);border-radius:var(--radius);padding:14px 16px;margin-bottom:12px;box-shadow:var(--shadow);position:relative;transition:transform .15s,box-shadow .15s}
.poi:hover{transform:translateY(-2px);box-shadow:0 14px 30px -16px rgba(18,48,61,.28)}
.poi::before{content:"";position:absolute;left:0;top:14px;bottom:14px;width:3px;border-radius:3px;background:linear-gradient(var(--sea),var(--dusk));opacity:.85}
.poi h3{margin:0 0 4px;font-size:16px;padding-left:6px}
.poi .src{font-size:12px;color:var(--ink-soft);font-weight:400;font-family:var(--font-sans)}
.poi .meta{color:var(--ink-soft);font-size:13px;padding-left:6px}
.poi p{padding-left:6px;margin:6px 0}
.tag{display:inline-block;background:#eef4f9;color:var(--sea-deep);font-size:12px;padding:2px 10px;border-radius:999px;margin:2px 4px 2px 0}
.actions{margin-top:10px;display:flex;gap:8px;flex-wrap:wrap;padding-left:6px}
.actions .nav{display:inline-block;text-decoration:none;background:var(--sea);color:#fff;padding:6px 14px;border-radius:999px;font-size:13px;transition:all .15s}
.actions .nav:hover{background:var(--sea-deep);transform:translateY(-1px)}
.actions .nav[style*="b06ae0"],.actions .nav[style*="background:#b06ae0"]{background:#8b5cf6}
.actions .nav[style*="b06ae0"]:hover{background:#7c3aed}
.sources{font-size:12px;color:var(--ink-soft);padding-left:6px;margin-top:6px}
.sources a{color:var(--sea);text-decoration:none;margin-right:8px}

/* ===== 地图 ===== */
#mapwrap{position:sticky;top:70px;height:calc(100vh - 90px);min-height:420px;border-radius:var(--radius);overflow:hidden;border:1px solid var(--line);box-shadow:var(--shadow)}
#map{width:100%;height:100%}
.mlegend{position:absolute;top:10px;left:10px;z-index:20;background:var(--glass);backdrop-filter:blur(6px);border:1px solid var(--line);border-radius:10px;padding:6px 10px;font-size:11.5px;color:var(--ink-soft);box-shadow:0 4px 12px -6px rgba(18,48,61,.25);pointer-events:none}
.mlegend i{display:inline-block;width:14px;height:4px;border-radius:2px;margin-right:4px;vertical-align:middle}
.mlegend i.p{background:var(--sea)}
.mlegend i.l{background:var(--sea);opacity:.5}

/* ===== 地图标注 ===== */
.seqmarker{width:28px;height:28px;border-radius:50%;background:var(--sea);color:#fff;font-size:13px;font-weight:700;text-align:center;line-height:28px;box-shadow:0 0 0 2px #fff,0 2px 8px rgba(18,48,61,.3)}
.poilabel{font-size:12px;background:rgba(255,255,255,.94);border:1px solid var(--line);border-radius:8px;padding:2px 8px;color:var(--ink);white-space:nowrap;box-shadow:0 2px 6px -2px rgba(18,48,61,.2)}
.hotelmark{width:28px;height:28px;border-radius:50%;background:#8b5cf6;color:#fff;font-size:15px;text-align:center;line-height:28px;box-shadow:0 0 0 2px #fff,0 2px 8px rgba(18,48,61,.3)}

/* ===== 顺序导航底部栏（玻璃） ===== */
#navbar{position:sticky;bottom:10px;left:0;right:0;z-index:50;background:var(--glass);backdrop-filter:blur(12px);border:1px solid var(--line);border-radius:14px;padding:10px 14px;display:flex;flex-direction:column;gap:8px;box-shadow:0 8px 30px -12px rgba(18,48,61,.35);margin:0 4px}
#navbar .navhead{font-weight:700;font-size:14px;color:var(--ink);display:flex;align-items:center;gap:8px}
#navbar .navhead::before{content:"";width:8px;height:8px;border-radius:50%;background:var(--dusk)}
#navbar .navtip{font-weight:400;color:var(--ink-soft);font-size:11.5px}
#navbar .chips{display:flex;gap:6px;flex-wrap:wrap}
#navbar .chip{font-size:12.5px;padding:5px 11px;border-radius:999px;border:1px solid var(--line);background:#fff;cursor:pointer;transition:all .15s}
#navbar .chip:hover{border-color:var(--sea)}
#navbar .chip.cur{background:var(--sea);color:#fff;border-color:var(--sea)}
#navbar .navctl{display:flex;gap:8px;align-items:center}
#navbar .navctl button{font-size:13px;padding:7px 14px;border-radius:10px;border:1px solid #bfdce6;background:#fff;color:var(--sea);cursor:pointer;transition:all .15s;font-family:var(--font-sans)}
#navbar .navctl button:hover{background:var(--sea);color:#fff}

/* ===== 手机端 ===== */
@media(max-width:960px){
  .topbar{flex-wrap:nowrap;overflow-x:auto;padding:10px 12px;margin:0 -14px 12px;scrollbar-width:none}
  .grid{grid-template-areas:"map" "content";grid-template-columns:1fr}
  .col-map{grid-area:map}
  #mapwrap{height:36vh;min-height:260px}
  #navbar{position:fixed;left:8px;right:8px;bottom:8px}
  #navbar .chips{flex-wrap:nowrap;overflow-x:auto;scrollbar-width:none;-webkit-overflow-scrolling:touch}
  body{padding-bottom:96px}
  .poilist li{padding:8px 0 8px 24px}
}
@media(max-width:560px){
  .dayhead{gap:10px}
  .daynum{width:38px;height:38px;font-size:15px;border-radius:12px}
}
</style></head><body>
<header><div class='hwrap'>
  <h1>__TITLE__ 之旅</h1>
  <div class='sub'>__SUBTITLE__</div>
  <div class='metachips'>__META_CHIPS__</div>
</div></header>
<div class='container'>
  <div class='topbar'>
    <button class='pill on' data-panel='trip'>📅 行程</button>
    <button class='pill' data-panel='stays'>🏨 住宿推荐</button>
    <button class='pill' data-panel='spots'>📍 景点指南</button>
    <button class='pill' data-panel='food'>🍜 餐饮指南</button>
    <button class='pill' data-panel='exp'>🎨 特色体验</button>
    <button class='pill' data-panel='prep'>🎒 出发前准备</button>
    <button class='pill' data-panel='tips'>⚠️ 旅行提醒</button>
    <button class='pill' data-panel='srcs'>📚 资料来源</button>
    <button class='pill' data-panel='import'>📦 导入路线</button>
  </div>
  <div class='grid'>
    <div class='col-content'>
      <div id='panel-trip' class='panel active'>__DAYCARDS__
        <div class='card note'>点选任意一天查看当日线路；在地图上点击编号可直达高德导航。住宿区域用紫色圈标出，不在逐日路线内。</div>
      </div>
      <div id='panel-spots' class='panel'><h2>📍 景点指南</h2>__POIHTML__</div>
      <div id='panel-food' class='panel'><h2>🍜 餐饮指南</h2><div class='note'>__FOOD_PLACEHOLDER__</div></div>
      <div id='panel-stays' class='panel'><h2>🏨 住宿推荐（按区域）</h2>__HOTEL_PLACEHOLDER__</div>
      <div id='panel-exp' class='panel'><h2>🎨 当地特色体验</h2>__EXP_PLACEHOLDER__</div>
      <div id='panel-prep' class='panel'><h2>🎒 出发前准备</h2><div class='note'>__PREP_PLACEHOLDER__</div></div>
      <div id='panel-tips' class='panel'><h2>⚠️ 旅行提醒</h2><div class='note'>__TIPS_PLACEHOLDER__</div></div>
      <div id='panel-srcs' class='panel'><h2>📚 资料来源（__SRC_COUNT__ 条）</h2>__SRC_PLACEHOLDER__</div>
      <div id='panel-import' class='panel'><h2>📦 把行程导入高德地图 / 旅行软件</h2>__IMPORT_PLACEHOLDER__</div>
    </div>
    <div class='col-map'><div id='mapwrap'><div class='mlegend'><i class='p'></i>当日路线 · <i class='l'></i>途经点 · <span style='color:#8b5cf6'>🏨 住宿区域</span></div><div id='mapnotice' class='mlegend' style='display:none;left:10px;top:38px;color:#a33'></div><div id='map'></div></div></div>
  </div>
</div>
<script src='https://webapi.amap.com/maps?v=2.0&key=__AMAPKEY__&plugin=AMap.Driving,AMap.Walking,AMap.Transfer'></script>
<script>
window.__DAYS__ = __MAPDAYS__;
window.__HOTELS__ = __HOTELS_JSON__;
(function(){ for(var d in window.__DAYS__){ var arr=window.__DAYS__[d]; arr.forEach(function(p,i){ p.seq=i+1; }); } })();
var mp = new AMap.Map('map',{zoom:11,center:[118.09,24.47]});
// 手机端地图兜底：高德脚本加载失败 / 初始化异常时给出提示，并延迟重绘保证容器尺寸稳定
function mapNotice(msg){ var n=document.getElementById('mapnotice'); if(n){ n.style.display='block'; n.textContent=msg; } }
window.addEventListener('error',function(e){
  if(e.target && e.target.tagName==='SCRIPT' && /webapi[.]amap/.test(e.target.src||'')){ mapNotice('高德地图脚本加载失败（网络或 Key 域名未授权）。仍可点各站点「导航」按钮直达高德。'); }
},true);
setTimeout(function(){
  if(!window.AMap){ mapNotice('高德地图未加载（通常为 Key 安全域名未包含本站，或网络原因）。仍可点各站点「导航」按钮直达高德。'); return; }
  try{ if(window.AMap.Map && typeof drawDay==='function'){ drawDay(activeDay); } }catch(err){}
},2500);
setTimeout(function(){
  if(window.AMap && mp && mp.getContainer && mp.getContainer().clientHeight===0){ try{ mp.resize && mp.resize(); }catch(err){} }
},600);
var routeLayers=[], markerLayers=[], activeDay=1;
function navUrl(p){ return 'https://uri.amap.com/navigation?to='+p.lng+','+p.lat+','+encodeURIComponent(p.name)+'&mode=car&callnative=1'; }
function clearLayers(){ routeLayers.concat(markerLayers).forEach(function(l){l.setMap&&l.setMap(null)}); routeLayers=[]; markerLayers=[]; }
function drawDay(d){
  clearLayers();
  var pts=(window.__DAYS__[d]||[]).filter(function(p){return p&&p.lat});
  if(pts.length<2) return;
  var path=pts.map(function(p){return [p.lng,p.lat]});
  var poly=new AMap.Polyline({path:path,strokeColor:'#0e7490',strokeWeight:6,strokeOpacity:.9,lineJoin:'round',borderWeight:2,strokeStyle:'solid'});
  poly.setMap(mp); routeLayers.push(poly);
  pts.forEach(function(p){
    var m=new AMap.Marker({position:[p.lng,p.lat],zIndex:120,content:'<div class="seqmarker" data-name="'+p.name+'">'+p.seq+'</div>',offset:new AMap.Pixel(-14,-14)});
    m.setMap(mp); markerLayers.push(m);
    var lb=new AMap.Text({position:[p.lng,p.lat],content:'<div class="poilabel">'+(p.seq+'. '+p.name)+'</div>',offset:new AMap.Pixel(0,12),zIndex:130});
    lb.setMap(mp); markerLayers.push(lb);
  });
  mp.setFitView([poly]);
  document.querySelectorAll('.daycard').forEach(function(c){ c.classList.toggle('on', +c.dataset.day===d); });
  renderNavbar(d, pts);
}
function renderNavbar(d, pts){
  var bar=document.getElementById('navbar'); if(!bar) return;
  var html='<div class="navhead">Day '+d+' 顺序导航 <span class="navtip">点站点直达高德 · 下一站自动前进</span></div>';
  html+='<div class="chips">';
  pts.forEach(function(p,i){ html+='<button class="chip" data-i="'+i+'">'+p.seq+'. '+p.name+'</button>'; });
  html+='</div><div class="navctl"><button id="prevStop">上一站</button><button id="nextStop">下一站</button></div>';
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
var hotelLayer=[];
(window.__HOTELS__||[]).forEach(function(h){
  if(!h.lat) return;
  var c=new AMap.Circle({center:[h.lng,h.lat],radius:h.radius||800,strokeColor:'#8b5cf6',strokeWeight:2,strokeOpacity:.6,fillColor:'#8b5cf6',fillOpacity:.16,zIndex:100});
  c.setMap(mp); hotelLayer.push(c);
  var m=new AMap.Marker({position:[h.lng,h.lat],zIndex:110,content:'<div class="hotelmark">🏨</div>',offset:new AMap.Pixel(-14,-14)});
  m.setMap(mp); hotelLayer.push(m);
  var lb=new AMap.Text({position:[h.lng,h.lat],content:'<div class="poilabel" style="border-color:#e0ccff;background:#faf5ff">🏨 '+h.name+'</div>',offset:new AMap.Pixel(0,16),zIndex:115});
  lb.setMap(mp); hotelLayer.push(lb);
  var _h=(function(hn){ return function(){ window.open('https://uri.amap.com/navigation?to='+h.lng+','+h.lat+','+encodeURIComponent(hn)+'&mode=car&callnative=1','_blank'); }; })(h.name);
  m.on('click',_h); lb.on('click',_h); c.on('click',_h);
});
var pois=document.querySelectorAll('.poi input[type=checkbox]');
pois.forEach(function(cb){cb.addEventListener('change',function(){ drawDay(activeDay); });});
var btns=document.querySelectorAll('.topbar .pill');
btns.forEach(function(b){b.addEventListener('click',function(){
  btns.forEach(function(x){x.classList.remove('on')});b.classList.add('on');
  document.querySelectorAll('.panel').forEach(function(p){p.classList.remove('active')});
  document.getElementById('panel-'+b.dataset.panel).classList.add('active');
  // 地图与顺序导航仅在「行程」栏显示；其他栏目隐藏地图列让内容占满
  var showMap=(b.dataset.panel==='trip');
  var grid=document.querySelector('.grid'); if(grid){ grid.classList.toggle('no-map', !showMap); }
  var bar=document.getElementById('navbar'); if(bar){ bar.style.display=showMap?'flex':'none'; }
  if(showMap){ setTimeout(function(){ try{ if(window.AMap){ mp.resize&&mp.resize(); drawDay(activeDay);} }catch(e){} },60); }
});});
</script>
<div id='navbar'></div>
</body></html>"""

def fill_demo(build=True):
    files = glob.glob(os.path.join(TRIP_DIR, "trip-*.json"))
    if not files:
        # 模板模式：无行程数据时输出说明页
        os.makedirs(SITE_DIR, exist_ok=True)
        html = HTML_TEMPLATE.replace("__AMAPKEY__", AMAP_JKEY) \
            .replace("__TITLE__", "旅行规划模板") \
            .replace("__SUBTITLE__", "还没有行程数据：请让 Agent 按 travel-research 流程生成 data/trips/trip-*.json 后重新运行本脚本") \
            .replace("__META_CHIPS__", "") \
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
        metachips = "".join(
            f"<span class='metachip'><b>{esc(k)}</b> {esc(v)}</span>"
            for k, v in [
                ("游玩", f"{trip['meta']['days']} 天"),
                ("日期", trip['meta']['dates'][0] + " ~ " + trip['meta']['dates'][-1]),
                ("出发", trip['meta']['departureCity']),
                ("人数", trip['meta']['travelers']),
                ("预算", trip['meta']['budget']),
            ])
        if trip["meta"].get("preferences"):
            metachips += "<span class='metachip'><b>偏好</b> " + esc(" / ".join(trip['meta']['preferences'])) + "</span>"
        metachips += "<span class='metachip'><b>节奏</b> " + esc(trip['meta'].get('pace', '')) + "</span>"
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
            hotel_pts.append({"name": h["name"], "lng": h["lng"], "lat": h["lat"], "radius": h.get("radius", 800)})
            badge = " ⭐推荐" if h.get("recommend") else ""
            srcs = "".join(f"<a href='{esc(s.get('url',''))}' target='_blank'>📎 {esc((s.get('title') or s.get('id'))[:30])}</a>" for s in [srcmap.get(sid) for sid in h.get("sourceIds", []) if srcmap.get(sid)])
            nav = f"<a class='nav' href='{route_url().format(to=f"{h['lng']},{h['lat']},{urllib.parse.quote(h['name'])}")}' target='_blank'>🧭 高德导航</a>"
            if h.get("poiId"):
                fav = f"<a class='nav' style='background:#b06ae0' href='https://uri.amap.com/poidetail?poiid={urllib.parse.quote(h['poiId'])}&callnative=1&src=travelsite' target='_blank'>⭐ 收藏</a>"
            else:
                fav = f"<a class='nav' style='background:#b06ae0' href='https://uri.amap.com/marker?position={h['lng']},{h['lat']}&name={urllib.parse.quote(h['name'])}&src=travelsite&coordinate=gaode' target='_blank'>📍 详情</a>"
            best = f"<div class='meta'>适合：{esc(h.get('bestFor',''))} · {esc(h.get('priceRange',''))}</div>"
            subs = ""
            if h.get("subHotels"):
                subs = "<div class='meta' style='color:#7b56a0'>候选示例：</div><p style='font-size:13px;color:#556'>" + " / ".join(esc(x) for x in h["subHotels"]) + "</p>"
            hotel_cards.append(f"<article class='poi'><h3>🏠 {esc(h['name'])}{badge} <span class='src'>{esc('区域')}</span></h3>"
                               f"<div class='meta'>{esc(h.get('area',''))}</div>{best}"
                               f"<p>{esc(h.get('notes',''))}</p>{subs}"
                               f"<div class='actions'>{nav} {fav}</div><div class='sources'>{srcs}</div></article>")
        hotels_html = "\n".join(hotel_cards) if hotel_cards else "<div class='note'>暂无住宿推荐数据。</div>"
        hotels_json = json.dumps(hotel_pts, ensure_ascii=False)
        html = HTML_TEMPLATE.replace("__AMAPKEY__", AMAP_JKEY).replace("__TITLE__", esc(title)).replace("__SUBTITLE__", esc(subtitles)).replace("__META_CHIPS__", metachips).replace("__POIHTML__", "\n".join(poi_card(p, route_url()) for p in trip["pois"]))
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
              <div class='dayhead'>
                <div class='daynum'>D{d}</div>
                <div class='dh-txt'>
                  <h2>{esc(day.get('theme',''))}</h2>
                  <div class='daymeta'>{esc(day.get('date',''))} · {esc(day.get('area',''))} · {esc(routeinfo)}</div>
                </div>
              </div>
              <ol class='poilist'>{''.join(blocks)}</ol>
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
