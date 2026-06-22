# AI算力产业链看板 · AI Supply Chain Dashboard

一个聚焦 **AI算力产业链** 的可视化看板：从算力芯片、光模块、PCB、先进封装到 AI新材料、物理AI等细分赛道，逐层罗列 A股与海外龙头标的，提供实时行情、K线、机构研报共识，并标注「最新方向」高景气赛道。

> 纯 Python 后端 + 单文件 HTML 前端，零框架、零数据库，`python server.py` 一键启动。

---

## ✨ 核心功能

- **5层产业链分层**：算力硬件 / 光通信 / PCB·载板 / 先进封装 / AI新材料 / 物理AI / AI软件 等十余个细分板块，每个板块罗列 A股 + 海外对标龙头。
- **实时行情**：A股走腾讯财经、海外走 Yahoo Finance，并发拉取，5分钟缓存。
- **K线图**：每只个股支持日/周/月 K线（A股前复权 + 海外），ECharts 绘制。
- **机构研报共识**：内置研报评级（买入/增持/中性）+ 机构一致预测 EPS（25/26/27年）。
- **研报库**：可检索的研报清单，支持点开原始 PDF（需自备 PDF 目录）。
- **最新方向**：首屏卡片展示近期新增的高景气赛道（AI新材料、物理AI、先进封装、半导体设备…）。
- **日间 / 夜间主题**，红涨绿跌（A股习惯）。

---

## 🚀 快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 启动（默认 8889 端口）
python server.py

# 3. 浏览器打开
open http://localhost:8889
```

自定义端口：`PORT=8000 python server.py`

---

## 🔌 API 接口

| 接口 | 说明 |
|------|------|
| `GET /api/stocks` | 全部板块的 A股+海外行情 + 研报共识（5分钟缓存） |
| `GET /api/refresh` | 强制刷新行情 |
| `GET /api/kline?code=300308&period=day&days=120` | A股 K线（前复权） |
| `GET /api/kline/intl?ticker=NVDA&period=day&bars=60` | 海外 K线 |
| `GET /api/reports` | 研报库清单 |
| `GET /report-pdf?f=xxx.pdf` | 打开研报原文（需配置 `REPORTS_DIR`） |

---

## 📦 技术栈

| 层 | 实现 |
|----|------|
| 后端 | Python 标准库 `http.server`（ThreadingHTTPServer），无 Web 框架 |
| 行情 | 腾讯财经 `qt.gtimg.cn`（A股）+ Yahoo Finance（`yfinance`，海外） |
| 研报 | 东方财富机构一致预测（预置于代码内） |
| 前端 | 单文件 `index.html`，原生 JS，无构建步骤 |
| 图表 | ECharts 5（本地 `echarts.min.js`） |

---

## 📁 目录结构

```
ai-supply-chain-dashboard/
├── server.py          # 后端：股票池 + 行情/K线抓取 + API
├── index.html         # 前端：产业链看板（单文件）
├── reports.json       # 研报库数据
├── echarts.min.js     # 图表库（本地化，避免CDN被墙）
├── requirements.txt
└── README.md
```

---

## 🔧 自定义

- **股票池**：编辑 `server.py` 顶部的 `A_STOCKS`（A股）和 `INTL_STOCKS`（海外）字典，按 `板块: {代码: 名称}` 组织。
- **研报共识**：编辑 `RESEARCH_CONSENSUS` 字典。
- **研报PDF**：设环境变量 `REPORTS_DIR=/path/to/pdfs` 指向你的研报PDF目录。

---

## ⚠️ 免责声明

本项目仅用于**技术研究与学习**，所有行情/研报数据来自第三方公开接口，可能存在延迟或错误。**不构成任何投资建议**，据此操作风险自负。请遵守数据来源方的使用条款，勿用于商业用途或高频请求。

---

## 📄 License

MIT
