#!/usr/bin/env python3
"""AI算力产业链看板 — 独立数据后端
拉取A股(腾讯财经)+海外(Yahoo Finance)行情、K线，提供研报共识数据。
"""

import os
import json, time, threading, urllib.parse
from http.server import HTTPServer, ThreadingHTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from datetime import datetime
import requests, yfinance as yf

RESEARCH_CONSENSUS = {
  "300308": {"reports":29,"buy":25,"hold":4,"neutral":0,"eps25":9.684,"eps26":26.92,"eps27":46.358},
  "300394": {"reports":18,"buy":15,"hold":3,"neutral":0,"eps25":2.589,"eps26":4.302,"eps27":5.651},
  "300502": {"reports":18,"buy":15,"hold":3,"neutral":0,"eps25":9.571,"eps26":18.601,"eps27":29.492},
  "002463": {"reports":19,"buy":14,"hold":5,"neutral":0,"eps25":1.986,"eps26":2.969,"eps27":4.517},
  "002916": {"reports":18,"buy":15,"hold":3,"neutral":0,"eps25":4.809,"eps26":7.914,"eps27":10.897},
  "002384": {"reports":10,"buy":9, "hold":1,"neutral":0,"eps25":0.757,"eps26":3.824,"eps27":7.368},
  "600183": {"reports":9, "buy":7, "hold":2,"neutral":0,"eps25":1.372,"eps26":2.325,"eps27":3.302},
  "688008": {"reports":16,"buy":11,"hold":5,"neutral":0,"eps25":1.829,"eps26":2.714,"eps27":3.578},
  "301308": {"reports":8, "buy":5, "hold":3,"neutral":0,"eps25":3.364,"eps26":29.449,"eps27":24.224},
  "688041": {"reports":28,"buy":23,"hold":5,"neutral":0,"eps25":1.095,"eps26":1.939,"eps27":2.887},
  "688256": {"reports":13,"buy":10,"hold":3,"neutral":0,"eps25":3.277,"eps26":12.624,"eps27":24.044},
  "603019": {"reports":18,"buy":15,"hold":3,"neutral":0,"eps25":1.487,"eps26":1.991,"eps27":2.477},
  "600941": {"reports":12,"buy":9, "hold":3,"neutral":0,"eps25":6.327,"eps26":6.135,"eps27":6.325},
  "000977": {"reports":17,"buy":13,"hold":4,"neutral":0,"eps25":1.643,"eps26":2.445,"eps27":3.278},
  "002837": {"reports":13,"buy":9, "hold":4,"neutral":0,"eps25":0.41, "eps26":1.442,"eps27":2.293},
  "002335": {"reports":8, "buy":6, "hold":2,"neutral":0,"eps25":0.559,"eps26":1.446,"eps27":2.009},
  "002230": {"reports":13,"buy":8, "hold":5,"neutral":0,"eps25":0.349,"eps26":0.516,"eps27":0.668},
  "300418": {"reports":9, "buy":6, "hold":3,"neutral":0,"eps25":-1.257,"eps26":-0.321,"eps27":0.103},
  "688327": {"reports":0, "buy":0, "hold":0,"neutral":0,"eps25":None,"eps26":None,"eps27":None},
  "688111": {"reports":31,"buy":24,"hold":7,"neutral":0,"eps25":3.963,"eps26":5.444,"eps27":5.683},
  "300058": {"reports":3, "buy":1, "hold":2,"neutral":0,"eps25":0.063,"eps26":0.07, "eps27":0.08},
  "301171": {"reports":7, "buy":7, "hold":0,"neutral":0,"eps25":0.256,"eps26":0.502,"eps27":0.703},
  "603598": {"reports":1, "buy":1, "hold":0,"neutral":0,"eps25":0.063,"eps26":0.3,  "eps27":0.4},
  "603533": {"reports":0, "buy":0, "hold":0,"neutral":0,"eps25":None,"eps26":None,"eps27":None},
  "300624": {"reports":6, "buy":3, "hold":3,"neutral":0,"eps25":-0.472,"eps26":0.227,"eps27":0.44},
  "300364": {"reports":3, "buy":2, "hold":1,"neutral":0,"eps25":-0.921,"eps26":0.027,"eps27":0.14},
  "300459": {"reports":0, "buy":0, "hold":0,"neutral":0,"eps25":None,"eps26":None,"eps27":None},
  "002241": {"reports":5, "buy":4, "hold":1,"neutral":0,"eps25":1.11, "eps26":0.978,"eps27":1.32},
  "002475": {"reports":14,"buy":10,"hold":4,"neutral":0,"eps25":2.278,"eps26":2.988,"eps27":3.827},
  "688608": {"reports":13,"buy":8, "hold":4,"neutral":1,"eps25":3.521,"eps26":4.291,"eps27":6.052},
  "603893": {"reports":15,"buy":12,"hold":3,"neutral":0,"eps25":2.47, "eps26":3.279,"eps27":4.193},
  "601360": {"reports":0, "buy":0, "hold":0,"neutral":0,"eps25":None,"eps26":None,"eps27":None},
  # ── 细分补充标的研报共识 ──
  "603986": {"reports":22,"buy":16,"hold":6,"neutral":0,"eps25":2.351,"eps26":6.866,"eps27":8.51},
  "601138": {"reports":19,"buy":14,"hold":5,"neutral":0,"eps25":1.778,"eps26":3.095,"eps27":4.193},
  "002938": {"reports":16,"buy":12,"hold":4,"neutral":0,"eps25":1.612,"eps26":2.355,"eps27":3.264},
  "000938": {"reports":14,"buy":7, "hold":7,"neutral":0,"eps25":0.589,"eps26":0.903,"eps27":1.178},
  "002273": {"reports":13,"buy":10,"hold":3,"neutral":0,"eps25":0.843,"eps26":1.042,"eps27":1.265},
  "300476": {"reports":13,"buy":10,"hold":3,"neutral":0,"eps25":4.388,"eps26":9.893,"eps27":16.631},
  "688037": {"reports":12,"buy":7, "hold":5,"neutral":0,"eps25":0.356,"eps26":1.162,"eps27":2.236},
  "300870": {"reports":12,"buy":7, "hold":4,"neutral":1,"eps25":1.599,"eps26":4.073,"eps27":5.746},
  "002851": {"reports":11,"buy":5, "hold":6,"neutral":0,"eps25":0.251,"eps26":1.595,"eps27":2.88},
  "300567": {"reports":11,"buy":7, "hold":4,"neutral":0,"eps25":0.293,"eps26":1.224,"eps27":2.05},
  "688120": {"reports":11,"buy":7, "hold":4,"neutral":0,"eps25":3.064,"eps26":4.059,"eps27":5.218},
  "688525": {"reports":10,"buy":8, "hold":2,"neutral":0,"eps25":1.812,"eps26":13.446,"eps27":14.798},
  "688313": {"reports":9, "buy":8, "hold":1,"neutral":0,"eps25":0.824,"eps26":1.596,"eps27":2.44},
  "688498": {"reports":9, "buy":7, "hold":2,"neutral":0,"eps25":1.534,"eps26":9.609,"eps27":16.171},
  "688147": {"reports":8, "buy":3, "hold":5,"neutral":0,"eps25":0.472,"eps26":0.794,"eps27":1.176},
  "603920": {"reports":7, "buy":5, "hold":2,"neutral":0,"eps25":0.949,"eps26":1.539,"eps27":2.333},
  "301536": {"reports":7, "buy":5, "hold":2,"neutral":0,"eps25":0.731,"eps26":1.261,"eps27":1.686},
  "688082": {"reports":6, "buy":4, "hold":2,"neutral":0,"eps25":2.893,"eps26":3.967,"eps27":4.843},
  "300604": {"reports":5, "buy":4, "hold":1,"neutral":0,"eps25":2.099,"eps26":3.37, "eps27":4.552},
  "300570": {"reports":5, "buy":3, "hold":2,"neutral":0,"eps25":1.316,"eps26":2.671,"eps27":4.494},
  "301018": {"reports":4, "buy":2, "hold":2,"neutral":0,"eps25":0.579,"eps26":1.622,"eps27":2.378},
  "688372": {"reports":4, "buy":3, "hold":1,"neutral":0,"eps25":1.804,"eps26":2.605,"eps27":3.61},
  "300474": {"reports":3, "buy":1, "hold":2,"neutral":0,"eps25":-0.315,"eps26":0.09, "eps27":0.227},
  "688047": {"reports":3, "buy":2, "hold":1,"neutral":0,"eps25":-1.135,"eps26":-0.46,"eps27":0.107},
  "300229": {"reports":1, "buy":1, "hold":0,"neutral":0,"eps25":-0.336,"eps26":-0.11,"eps27":-0.05},
  # ── 物理AI / 人形机器人研报共识 ──
  "601689": {"reports":26,"buy":21,"hold":5,"neutral":0,"eps25":1.599,"eps26":1.948,"eps27":2.364},
  "601100": {"reports":24,"buy":18,"hold":6,"neutral":0,"eps25":2.039,"eps26":2.61, "eps27":3.207},
  "002050": {"reports":19,"buy":13,"hold":6,"neutral":0,"eps25":0.966,"eps26":1.133,"eps27":1.325},
  "688017": {"reports":12,"buy":3, "hold":9,"neutral":0,"eps25":0.678,"eps26":1.056,"eps27":1.544},
  "002472": {"reports":8, "buy":6, "hold":2,"neutral":0,"eps25":1.484,"eps26":1.71, "eps27":2.009},
  "002979": {"reports":7, "buy":4, "hold":3,"neutral":0,"eps25":0.716,"eps26":0.99, "eps27":1.257},
  "603667": {"reports":2, "buy":1, "hold":1,"neutral":0,"eps25":0.239,"eps26":0.435,"eps27":0.585},
}

# ───────────────────────────────────────────────
#  股票配置
# ───────────────────────────────────────────────

A_STOCKS = {
    # ── AI硬件 ──
    # ══ AI新材料（雪球产业链：PCB材料/MLCC/封装填料/光芯片/半导体材料）══
    "sz301217": {"name":"铜冠铜箔","tab":"material","sector":"PCB铜箔(HVLP)"},
    "sh603186": {"name":"华正新材","tab":"material","sector":"PCB材料/CBF膜"},
    "sh601208": {"name":"东材科技","tab":"material","sector":"低介电树脂"},
    "sh605589": {"name":"圣泉集团","tab":"material","sector":"电子级树脂"},
    "sh603002": {"name":"宏昌电子","tab":"material","sector":"封装增层膜(GBF)"},
    "sh688550": {"name":"瑞联新材","tab":"material","sector":"电子化学品"},
    "sh688300": {"name":"联瑞新材","tab":"material","sector":"封装填料/硅微粉"},
    "sz301373": {"name":"凌玮科技","tab":"material","sector":"封装填料/球硅"},
    "sh688733": {"name":"壹石通",  "tab":"material","sector":"封装填料/氧化铝"},
    "sz300285": {"name":"国瓷材料","tab":"material","sector":"MLCC陶瓷粉"},
    "sz000636": {"name":"风华高科","tab":"material","sector":"MLCC电容"},
    "sz300319": {"name":"麦捷科技","tab":"material","sector":"MLCC/电感"},
    "sh603678": {"name":"火炬电子","tab":"material","sector":"特种MLCC"},
    "sz300408": {"name":"三环集团","tab":"material","sector":"MLCC/陶瓷封装"},
    "sh688183": {"name":"生益电子","tab":"material","sector":"封装基板"},
    "sh688409": {"name":"富创精密","tab":"material","sector":"封装零部件"},
    "sz300684": {"name":"中石科技","tab":"material","sector":"导热界面材料"},
    "sz002674": {"name":"兴业科技","tab":"material","sector":"磷化铟衬底"},
    "sh600255": {"name":"鑫科材料","tab":"material","sector":"铜基/高速铜连接"},
    "sh688195": {"name":"腾景科技","tab":"material","sector":"精密光学元件"},
    "sz300221": {"name":"银禧科技","tab":"material","sector":"改性塑料"},
    "sh688381": {"name":"呈和科技","tab":"material","sector":"AI阻燃剂/树脂"},
    "sz300346": {"name":"南大光电","tab":"material","sector":"光刻胶/前驱体"},
    "sz300655": {"name":"晶瑞电材","tab":"material","sector":"光刻胶/化学品"},
    "sh688019": {"name":"安集科技","tab":"material","sector":"CMP抛光液"},
    "sz300054": {"name":"鼎龙股份","tab":"material","sector":"CMP抛光垫"},
    "sh688146": {"name":"中船特气","tab":"material","sector":"电子特气(NF3)"},
    "sh688432": {"name":"有研硅",  "tab":"material","sector":"半导体硅片/靶材"},
    "sz300666": {"name":"江丰电子","tab":"material","sector":"溅射靶材"},
    "sz300706": {"name":"阿石创",  "tab":"material","sector":"PVD镀膜靶材"},
    "sz002957": {"name":"科瑞技术","tab":"material","sector":"测试自动化设备"},
    "sh688478": {"name":"晶升股份","tab":"material","sector":"碳化硅长晶炉"},
    "sh688227": {"name":"品高股份","tab":"material","sector":"云计算/算力"},
    "sh688515": {"name":"裕太微",  "tab":"material","sector":"以太网PHY芯片"},
    "sz300943": {"name":"春晖智控","tab":"material","sector":"液冷控制阀"},
    "sz301687": {"name":"新广益",  "tab":"material","sector":"PCB设备/新材料"},
    "bj920083": {"name":"金戈新材","tab":"material","sector":"新材料(北交所)"},
    "bj920009": {"name":"丹娜生物","tab":"material","sector":"新材料(北交所)"},
    "sz300166": {"name":"东方国信","tab":"material","sector":"大数据/AI应用"},
    "sh688485": {"name":"九州一轨","tab":"material","sector":"阻尼材料"},
    "sz300308": {"name":"中际旭创","tab":"optics","sector":"光模块"},
    "sz300394": {"name":"天孚通信","tab":"optics","sector":"光模块"},
    "sz300502": {"name":"新易盛",  "tab":"optics","sector":"光模块"},
    "sz002463": {"name":"沪电股份","tab":"pcb",   "sector":"PCB"},
    "sz002916": {"name":"深南电路","tab":"pcb",   "sector":"PCB"},
    "sz002384": {"name":"东山精密","tab":"pcb",   "sector":"PCB"},
    "sh600183": {"name":"生益科技","tab":"pcb",   "sector":"PCB"},
    "sh688008": {"name":"澜起科技","tab":"hbm",   "sector":"HBM/存储"},
    "sz301308": {"name":"江波龙",  "tab":"hbm",   "sector":"HBM/存储"},
    "sh688041": {"name":"海光信息","tab":"cpugpu","sector":"CPU/GPU"},
    "sh688256": {"name":"寒武纪",  "tab":"cpugpu","sector":"CPU/GPU"},
    "sh603019": {"name":"中科曙光","tab":"downstream","sector":"下游企业"},
    "sh600941": {"name":"中国移动","tab":"downstream","sector":"下游企业"},
    "sz000977": {"name":"浪潮信息","tab":"downstream","sector":"下游企业"},
    "sz002837": {"name":"英维克",  "tab":"energy","sector":"算力能源"},
    "sz002335": {"name":"科华数据","tab":"energy","sector":"算力能源"},
    # ── AI软件 ──
    "sz002230": {"name":"科大讯飞","tab":"aimodel",   "sector":"AI大模型"},
    "sz300418": {"name":"昆仑万维","tab":"aimodel",   "sector":"AI大模型"},
    "sh601360": {"name":"三六零",  "tab":"aimodel",   "sector":"AI大模型"},
    "sh688327": {"name":"云从科技","tab":"aimodel",   "sector":"AI大模型"},
    "sh688111": {"name":"金山办公","tab":"aimodel",   "sector":"AI大模型"},
    "sz300058": {"name":"蓝色光标","tab":"aimarketing","sector":"AI营销"},
    "sz301171": {"name":"易点天下","tab":"aimarketing","sector":"AI营销"},
    "sh603598": {"name":"引力传媒","tab":"aimarketing","sector":"AI营销"},
    "sh603533": {"name":"掌阅科技","tab":"aicomics",  "sector":"AI漫剧"},
    "sz300624": {"name":"万兴科技","tab":"aicomics",  "sector":"AI漫剧"},
    "sz300364": {"name":"中文在线","tab":"aicomics",  "sector":"AI漫剧"},
    "sz300459": {"name":"汤姆猫",  "tab":"aicomics",  "sector":"AI漫剧"},
    "sz002241": {"name":"歌尔股份","tab":"aiglasses",  "sector":"AI眼镜"},
    "sz002475": {"name":"立讯精密","tab":"aiglasses",  "sector":"AI眼镜"},
    "sh688608": {"name":"恒玄科技","tab":"aiglasses",  "sector":"AI眼镜"},
    "sh603893": {"name":"瑞芯微",  "tab":"aiglasses",  "sector":"AI眼镜"},
    # ── 先进封装 ──
    "sh600584": {"name":"长电科技","tab":"advpkg","sector":"先进封装"},
    "sz002156": {"name":"通富微电","tab":"advpkg","sector":"先进封装"},
    "sz002185": {"name":"华天科技","tab":"advpkg","sector":"先进封装"},
    "sh688362": {"name":"甬矽电子","tab":"advpkg","sector":"先进封装"},
    # ── 半导体设备/材料 ──
    "sz002371": {"name":"北方华创","tab":"semieq","sector":"半导体设备"},
    "sh688012": {"name":"中微公司","tab":"semieq","sector":"半导体设备"},
    "sh688072": {"name":"拓荆科技","tab":"semieq","sector":"半导体设备"},
    "sh688361": {"name":"中科飞测","tab":"semieq","sector":"量检测设备"},
    "sz002409": {"name":"雅克科技","tab":"semieq","sector":"半导体材料"},
    # ══ 细分领域补充标的（基于研报）══
    # 光模块
    "sz300570": {"name":"太辰光",  "tab":"optics","sector":"光纤组件"},
    "sh688498": {"name":"源杰科技","tab":"optics","sector":"EML激光芯片"},
    "sh688313": {"name":"仕佳光子","tab":"optics","sector":"光芯片"},
    # PCB
    "sz300476": {"name":"胜宏科技","tab":"pcb","sector":"AI主板"},
    "sz002938": {"name":"鹏鼎控股","tab":"pcb","sector":"FPC柔性板"},
    "sh603920": {"name":"世运电路","tab":"pcb","sector":"AI主板"},
    # HBM/存储
    "sh603986": {"name":"兆易创新","tab":"hbm","sector":"DRAM/NOR"},
    "sh688525": {"name":"佰维存储","tab":"hbm","sector":"存储模组"},
    # CPU/GPU
    "sh688047": {"name":"龙芯中科","tab":"cpugpu","sector":"国产CPU"},
    "sz300474": {"name":"景嘉微",  "tab":"cpugpu","sector":"国产GPU"},
    # 先进封装
    "sh603005": {"name":"晶方科技","tab":"advpkg","sector":"晶圆级封装"},
    "sh688372": {"name":"伟测科技","tab":"advpkg","sector":"封测代工"},
    # 半导体设备
    "sh688037": {"name":"芯源微",  "tab":"semieq","sector":"涂胶显影"},
    "sh688120": {"name":"华海清科","tab":"semieq","sector":"CMP设备"},
    "sh688082": {"name":"盛美上海","tab":"semieq","sector":"清洗设备"},
    "sz300567": {"name":"精测电子","tab":"semieq","sector":"量检测设备"},
    "sz300604": {"name":"长川科技","tab":"semieq","sector":"测试设备"},
    "sh688147": {"name":"微导纳米","tab":"semieq","sector":"薄膜沉积"},
    # 算力能源
    "sz301018": {"name":"申菱环境","tab":"energy","sector":"液冷散热"},
    "sz300499": {"name":"高澜股份","tab":"energy","sector":"液冷散热"},
    "sz300870": {"name":"欧陆通",  "tab":"energy","sector":"服务器电源"},
    "sz002851": {"name":"麦格米特","tab":"energy","sector":"服务器电源"},
    # 下游企业
    "sh601138": {"name":"工业富联","tab":"downstream","sector":"AI服务器ODM"},
    "sz000938": {"name":"紫光股份","tab":"downstream","sector":"AI服务器整机"},
    # AI眼镜
    "sz002273": {"name":"水晶光电","tab":"aiglasses","sector":"光学器件"},
    "sz301536": {"name":"星宸科技","tab":"aiglasses","sector":"SoC芯片"},
    "sz300622": {"name":"博士眼镜","tab":"aiglasses","sector":"渠道"},
    # AI大模型
    "sz300229": {"name":"拓尔思",  "tab":"aimodel","sector":"NLP/大模型"},
    # AI营销
    "sz002400": {"name":"省广集团","tab":"aimarketing","sector":"AI广告"},
    # ══ 物理AI / 人形机器人 ══
    "sz002050": {"name":"三花智控","tab":"robot","sector":"整机Tier1"},
    "sh601689": {"name":"拓普集团","tab":"robot","sector":"整机Tier1"},
    "sh688017": {"name":"绿的谐波","tab":"robot","sector":"减速器"},
    "sz002472": {"name":"双环传动","tab":"robot","sector":"减速器"},
    "sh601100": {"name":"恒立液压","tab":"robot","sector":"丝杠"},
    "sh603667": {"name":"五洲新春","tab":"robot","sector":"丝杠"},
    "sh603728": {"name":"鸣志电器","tab":"robot","sector":"电机"},
    "sz003021": {"name":"兆威机电","tab":"robot","sector":"灵巧手"},
    "sz300007": {"name":"汉威科技","tab":"robot","sector":"传感器"},
    "sz002979": {"name":"雷赛智能","tab":"robot","sector":"灵巧手"},
}

INTL_STOCKS = {
    # 光模块 / 光器件
    "COHR": {"name":"Coherent",    "cn":"Coherent", "sector":"光模块","country":"🇺🇸 美股"},
    "LITE": {"name":"Lumentum",    "cn":"Lumentum", "sector":"光模块","country":"🇺🇸 美股"},
    "MTSI": {"name":"MACOM",       "cn":"MACOM",    "sector":"光模块","country":"🇺🇸 美股"},
    "5801.T":{"name":"Sumitomo Elec","cn":"住友电工","sector":"光模块","country":"🇯🇵 日股"},
    # GPU / 芯片
    "NVDA": {"name":"NVIDIA",      "cn":"英伟达",   "sector":"CPU/GPU","country":"🇺🇸 美股"},
    "AMD":  {"name":"AMD",         "cn":"AMD",      "sector":"CPU/GPU","country":"🇺🇸 美股"},
    # 存储
    "MU":   {"name":"Micron",      "cn":"美光",     "sector":"HBM/存储","country":"🇺🇸 美股"},
    "000660.KS":{"name":"SK Hynix","cn":"SK海力士", "sector":"HBM/存储","country":"🇰🇷 韩股"},
    # PCB / 封装基板
    "TTMI": {"name":"TTM Tech",    "cn":"TTM",      "sector":"PCB","country":"🇺🇸 美股"},
    "6794.T":{"name":"Ibiden",     "cn":"揖斐电",   "sector":"PCB","country":"🇯🇵 日股"},
    # 散热 / 能源
    "VRT":  {"name":"Vertiv",      "cn":"Vertiv",   "sector":"算力能源","country":"🇺🇸 美股"},
    "ETN":  {"name":"Eaton",       "cn":"伊顿",     "sector":"算力能源","country":"🇺🇸 美股"},
    # 服务器 ODM
    "SMCI": {"name":"Super Micro", "cn":"超微电脑", "sector":"下游企业","country":"🇺🇸 美股"},
    # 先进封装
    "TSM":  {"name":"TSMC",        "cn":"台积电",   "sector":"先进封装","country":"🇺🇸 美股"},
    "ASX":  {"name":"ASE",         "cn":"日月光",   "sector":"先进封装","country":"🇺🇸 美股"},
    "AMKR": {"name":"Amkor",       "cn":"安靠",     "sector":"先进封装","country":"🇺🇸 美股"},
    # 半导体设备
    "ASML": {"name":"ASML",        "cn":"阿斯麦",   "sector":"半导体设备","country":"🇺🇸 美股"},
    "AMAT": {"name":"Applied Mat", "cn":"应用材料", "sector":"半导体设备","country":"🇺🇸 美股"},
    "LRCX": {"name":"Lam Research", "cn":"泛林",    "sector":"半导体设备","country":"🇺🇸 美股"},
    "KLAC": {"name":"KLA",         "cn":"科磊",     "sector":"半导体设备","country":"🇺🇸 美股"},
    # ── AI软件 海外对标 ──
    # AI大模型
    "MSFT": {"name":"Microsoft",   "cn":"微软",     "sector":"AI大模型","country":"🇺🇸 美股"},
    "GOOGL":{"name":"Alphabet",    "cn":"谷歌",     "sector":"AI大模型","country":"🇺🇸 美股"},
    "PLTR": {"name":"Palantir",    "cn":"Palantir", "sector":"AI大模型","country":"🇺🇸 美股"},
    # AI营销
    "TTD":  {"name":"Trade Desk",  "cn":"The Trade Desk","sector":"AI营销","country":"🇺🇸 美股"},
    "APP":  {"name":"AppLovin",    "cn":"AppLovin", "sector":"AI营销","country":"🇺🇸 美股"},
    "PINS": {"name":"Pinterest",   "cn":"Pinterest","sector":"AI营销","country":"🇺🇸 美股"},
    # AI漫剧/AIGC
    "ADBE": {"name":"Adobe",       "cn":"Adobe",    "sector":"AIGC","country":"🇺🇸 美股"},
    "RBLX": {"name":"Roblox",      "cn":"Roblox",   "sector":"AIGC","country":"🇺🇸 美股"},
    "NFLX": {"name":"Netflix",     "cn":"奈飞",     "sector":"AIGC","country":"🇺🇸 美股"},
    # AI眼镜
    "META": {"name":"Meta",        "cn":"Meta",     "sector":"AI眼镜","country":"🇺🇸 美股"},
    "AAPL": {"name":"Apple",       "cn":"苹果",     "sector":"AI眼镜","country":"🇺🇸 美股"},
    "QCOM": {"name":"Qualcomm",    "cn":"高通",     "sector":"AI眼镜","country":"🇺🇸 美股"},
    # 物理AI / 人形机器人 海外对标
    "TSLA": {"name":"Tesla",       "cn":"特斯拉",   "sector":"人形机器人","country":"🇺🇸 美股"},
    "6954.T":{"name":"FANUC",      "cn":"发那科",   "sector":"工业机器人","country":"🇯🇵 日股"},
    "6506.T":{"name":"Yaskawa",     "cn":"安川电机", "sector":"工业机器人","country":"🇯🇵 日股"},
}

# ───────────────────────────────────────────────
#  Tencent Finance 字段位置 (经验证)
# ───────────────────────────────────────────────
F_NAME   = 1
F_CODE   = 2
F_PRICE  = 3
F_PCLOSE = 4
F_CHG    = 31   # 涨跌额
F_PCHG   = 32   # 涨跌幅%
F_HIGH   = 33
F_LOW    = 34
F_TURN   = 38   # 换手率%
F_PE     = 39   # 市盈率(动)
F_MCAP   = 44   # 总市值(亿元)
F_PB     = 46   # 市净率
F_52H    = 47   # 52周高
F_52L    = 48   # 52周低

def fv(parts, idx, default=None):
    try:
        v = parts[idx].strip()
        return float(v) if v else default
    except:
        return default

# ───────────────────────────────────────────────
#  数据拉取
# ───────────────────────────────────────────────

def fetch_a_stocks():
    tickers = list(A_STOCKS.keys())
    url = "http://qt.gtimg.cn/q=" + ",".join(tickers)
    try:
        r = requests.get(url, timeout=10,
                         headers={"User-Agent":"Mozilla/5.0",
                                  "Referer":"https://finance.qq.com"})
        r.encoding = "gbk"
        result = {}
        for line in r.text.strip().split('\n'):
            if '="' not in line:
                continue
            raw_key = line.split('="')[0].strip().lstrip('v_')
            data_str = line.split('"')[1] if '"' in line else ""
            parts = data_str.split('~')
            if len(parts) < 50:
                continue
            cfg = A_STOCKS.get(raw_key, {})
            price   = fv(parts, F_PRICE)
            pclose  = fv(parts, F_PCLOSE)
            pchg    = fv(parts, F_PCHG)
            code    = raw_key.lstrip('sz').lstrip('sh')
            result[code] = {
                "name":    cfg.get("name", parts[F_NAME]),
                "price":   price,
                "pclose":  pclose,
                "change":  fv(parts, F_CHG),
                "pchg":    pchg,
                "high":    fv(parts, F_HIGH),
                "low":     fv(parts, F_LOW),
                "turn":    fv(parts, F_TURN),
                "pe":      fv(parts, F_PE),
                "pb":      fv(parts, F_PB),
                "mcap":    fv(parts, F_MCAP),   # 亿元
                "w52h":    fv(parts, F_52H),
                "w52l":    fv(parts, F_52L),
                "tab":     cfg.get("tab",""),
                "sector":  cfg.get("sector",""),
                "currency":"CNY",
            }
        return result
    except Exception as e:
        print(f"[A-stock] {e}")
        return {}

def _fetch_one_intl(item):
    ticker, cfg = item
    try:
        info = yf.Ticker(ticker).info
        price  = info.get("currentPrice") or info.get("regularMarketPrice") or 0
        prev   = info.get("regularMarketPreviousClose") or 0
        pchg   = (price - prev) / prev * 100 if prev else 0
        mcap   = info.get("marketCap") or 0
        return ticker, {
            "name":    cfg["name"],
            "cn":      cfg["cn"],
            "sector":  cfg["sector"],
            "country": cfg["country"],
            "price":   round(price, 2),
            "pchg":    round(pchg, 2),
            "pe":      round(info.get("trailingPE") or 0, 1),
            "pb":      round(info.get("priceToBook") or 0, 2),
            "mcap":    mcap,
            "currency":info.get("currency","USD"),
            "rev_growth": round((info.get("revenueGrowth") or 0)*100, 1),
        }
    except Exception as e:
        print(f"[intl] {ticker}: {e}")
        return ticker, None

def fetch_intl_stocks():
    """并发拉取海外股票（20只并行，~5秒完成，避免串行40秒+）"""
    from concurrent.futures import ThreadPoolExecutor
    result = {}
    with ThreadPoolExecutor(max_workers=12) as ex:
        for ticker, data in ex.map(_fetch_one_intl, INTL_STOCKS.items()):
            if data:
                result[ticker] = data
    return result

# ───────────────────────────────────────────────
#  Cache
# ───────────────────────────────────────────────
_cache = {"data": None, "ts": 0}
_lock  = threading.Lock()
TTL    = 300  # 5 min

def get_data(force=False):
    with _lock:
        now = time.time()
        if not force and _cache["data"] and now - _cache["ts"] < TTL:
            return _cache["data"]
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 正在拉取最新行情...")
        a  = fetch_a_stocks()
        il = fetch_intl_stocks()
        # 保留旧缓存中的数据，防止API临时故障覆盖好数据
        prev = _cache.get("data") or {}
        if not a and prev.get("a_stocks"):
            print("  ⚠️  A股拉取失败，保留上次数据")
            a = prev["a_stocks"]
        if not il and prev.get("intl_stocks"):
            print("  ⚠️  国际股拉取失败，保留上次数据")
            il = prev["intl_stocks"]
        data = {
            "a_stocks":    a,
            "intl_stocks": il,
            "research":    RESEARCH_CONSENSUS,
            "ts":  datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "src": "腾讯财经 + Yahoo Finance + 东方财富研报",
        }
        _cache["data"] = data
        _cache["ts"]   = now
        print(f"  A股 {len(a)} 只，国际 {len(il)} 只 拉取完成")
        return data

# ───────────────────────────────────────────────
#  K线数据
# ───────────────────────────────────────────────

_kline_cache = {}
KLINE_TTL = 1800  # 30 min

def fetch_kline(code: str, days: int = 120, period: str = "day"):
    """从腾讯财经拉取前复权K线，period: day/week/month，days=请求的K线条数，返回 [{date,open,close,high,low,vol}, ...]"""
    cache_key = f"{code}_{period}_{days}"
    now = time.time()
    if cache_key in _kline_cache:
        cached_data, cached_ts = _kline_cache[cache_key]
        if now - cached_ts < KLINE_TTL:
            return cached_data
    # 确定市场前缀
    prefix = "sh" if (code.startswith("6") or code.startswith("9") or code.startswith("5")) else "sz"
    full_code = f"{prefix}{code}"
    url = f"https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param={full_code},{period},,,{days},qfq"
    try:
        r = requests.get(url, timeout=12, headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
            "Referer": "https://finance.qq.com",
        })
        raw = r.text.strip()
        # 响应格式：{"code":0,"data":{"sz300308":{"qfqday":[...], "qfqweek":[...]}}}
        data_obj = json.loads(raw)
        code_data = data_obj.get("data", {}).get(full_code, {})
        # 周K字段名: qfqweek, 月K: qfqmonth，日K: qfqday
        key_map = {"day": "qfqday", "week": "qfqweek", "month": "qfqmonth"}
        rows = code_data.get(key_map.get(period, "qfqday")) or code_data.get(period) or []
        result = []
        for item in rows:
            if len(item) >= 6:
                try:
                    result.append({
                        "date":  item[0],
                        "open":  round(float(item[1]), 3),
                        "close": round(float(item[2]), 3),
                        "high":  round(float(item[3]), 3),
                        "low":   round(float(item[4]), 3),
                        "vol":   round(float(item[5])),
                    })
                except (ValueError, TypeError):
                    continue
        _kline_cache[cache_key] = (result, now)
        return result
    except Exception as e:
        print(f"[kline] {code}: {e}")
        return []

# ───────────────────────────────────────────────
#  国际股票 K线（yfinance）
# ───────────────────────────────────────────────
_kline_intl_cache = {}
KLINE_INTL_TTL = 1800  # 30 min

def fetch_kline_intl(ticker: str, bars: int = 60, period: str = "day"):
    """国际股K线：直连 Yahoo Chart API（0.3秒 vs yfinance库8秒），美股/日股/韩股统一"""
    import datetime
    cache_key = f"{ticker}_{period}_{bars}"
    now = time.time()
    if cache_key in _kline_intl_cache:
        cached, ts = _kline_intl_cache[cache_key]
        if now - ts < KLINE_INTL_TTL:
            return cached
    # 取足够长的范围，再截取最近 bars 根
    range_map    = {"day": "1y", "week": "5y", "month": "10y"}
    interval_map = {"day": "1d", "week": "1wk", "month": "1mo"}
    rng = range_map.get(period, "1y")
    itv = interval_map.get(period, "1d")
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?range={rng}&interval={itv}"
    try:
        r = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        res = json.loads(r.text)["chart"]["result"][0]
        ts_list = res["timestamp"]
        q = res["indicators"]["quote"][0]
        o, c, h, l, v = q["open"], q["close"], q["high"], q["low"], q["volume"]
        result = []
        for i in range(len(ts_list)):
            if c[i] is None or o[i] is None:
                continue  # 跳过停牌/空值
            result.append({
                "date":  str(datetime.date.fromtimestamp(ts_list[i])),
                "open":  round(float(o[i]), 3),
                "close": round(float(c[i]), 3),
                "high":  round(float(h[i]), 3),
                "low":   round(float(l[i]), 3),
                "vol":   int(v[i] or 0),
            })
        result = result[-bars:]  # 最近 bars 根
        if result:
            _kline_intl_cache[cache_key] = (result, now)
        return result
    except Exception as e:
        print(f"[kline_intl] {ticker}: {e}")
        return []

# ───────────────────────────────────────────────
#  HTTP Server
# ───────────────────────────────────────────────
DIR = Path(__file__).parent

# 研报库数据（启动时加载一次）
try:
    REPORTS = json.loads((DIR / "reports.json").read_text(encoding="utf-8"))
    print(f"   📑 研报库已加载 {len(REPORTS)} 篇")
except Exception as e:
    print(f"   ⚠️ 研报库加载失败: {e}")
    REPORTS = []

class H(BaseHTTPRequestHandler):
    def log_message(self, *a): pass

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        p = parsed.path

# ───────────────────────────────────────────────
#  HTTP 服务（精简版：仅 AI产业链相关接口）
# ───────────────────────────────────────────────
DIR = Path(__file__).parent
try:
    REPORTS = json.loads((DIR / "reports.json").read_text(encoding="utf-8"))
    print(f"   研报库已加载 {len(REPORTS)} 篇")
except Exception:
    REPORTS = []

class H(BaseHTTPRequestHandler):
    def log_message(self, *a): pass

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path); p = parsed.path
        if p == "/api/stocks":
            self._json(get_data())
        elif p == "/api/refresh":
            self._json(get_data(force=True))
        elif p == "/api/reports":
            self._json({"reports": REPORTS, "count": len(REPORTS)})
        elif p == "/api/kline":
            qs = urllib.parse.parse_qs(parsed.query)
            code = (qs.get("code") or [""])[0].strip()
            days = int((qs.get("days") or ["120"])[0])
            period = (qs.get("period") or ["day"])[0].strip()
            if period not in ("day", "week", "month"): period = "day"
            self._json({"code": code, "kline": fetch_kline(code, days, period)} if code else {"error": "missing code"})
        elif p == "/api/kline/intl":
            qs = urllib.parse.parse_qs(parsed.query)
            ticker = (qs.get("ticker") or [""])[0].strip()
            bars = int((qs.get("bars") or ["60"])[0])
            period = (qs.get("period") or ["day"])[0].strip()
            if period not in ("day", "week", "month"): period = "day"
            self._json({"ticker": ticker, "kline": fetch_kline_intl(ticker, bars, period)} if ticker else {"error": "missing ticker"})
        elif p == "/report-pdf":
            qs = urllib.parse.parse_qs(parsed.query)
            self._serve_pdf((qs.get("f") or [""])[0])
        elif p in ("/", "/index.html"):
            self._file("index.html", "text/html;charset=utf-8")
        else:
            fp = (DIR / p.lstrip("/")).resolve()
            if fp.is_file() and fp.is_relative_to(DIR.resolve()):
                mt = "text/css" if p.endswith(".css") else "application/javascript" if p.endswith(".js") else \
                     "application/json" if p.endswith(".json") else "text/html;charset=utf-8"
                self._file(p.lstrip("/"), mt)
            else:
                self.send_error(404)

    def _serve_pdf(self, fname):
        # 研报PDF目录（环境变量 REPORTS_DIR 指定；开源版默认不含PDF文件）
        rpt_dir = Path(os.environ.get("REPORTS_DIR", str(DIR / "reports")))
        safe = os.path.basename(fname); fp = rpt_dir / safe
        if not safe.endswith(".pdf") or not fp.exists():
            self.send_error(404, "PDF not found"); return
        try:
            data = fp.read_bytes()
            self.send_response(200); self.send_header("Content-Type", "application/pdf")
            self.send_header("Content-Length", len(data)); self.end_headers(); self.wfile.write(data)
        except Exception as e:
            self.send_error(500, str(e))

    def _json(self, obj):
        b = json.dumps(obj, ensure_ascii=False).encode()
        self.send_response(200); self.send_header("Content-Type", "application/json;charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*"); self.send_header("Content-Length", len(b))
        self.end_headers(); self.wfile.write(b)

    def _file(self, name, mime):
        try:
            d = (DIR / name).read_bytes()
            self.send_response(200); self.send_header("Content-Type", mime)
            self.send_header("Content-Length", len(d)); self.end_headers(); self.wfile.write(d)
        except Exception as e:
            self.send_error(500, str(e))

if __name__ == "__main__":
    PORT = int(os.environ.get("PORT", 8889))
    print("AI算力产业链看板")
    print(f"   访问: http://localhost:{PORT}")
    threading.Thread(target=lambda: get_data(), daemon=True).start()
    ThreadingHTTPServer(("", PORT), H).serve_forever()
