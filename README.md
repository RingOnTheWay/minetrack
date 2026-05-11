# MC Stats - Minecraft 服务器数据统计

基于 Flask + Chart.js 的 Minecraft 服务器数据统计面板，支持本地数据扫描导入和静态页面部署两种模式。

## 项目结构

```
stat/
├── index.html              # 前端页面（Material You Design 风格）
├── chart.js                # Chart.js 图表库
├── data.json               # 导出的静态统计数据
├── mc_stats.db             # SQLite 数据库（本地模式）
├── mc_stats_server.py      # Flask 后端服务
├── scripts/
│   └── export_data.py      # 数据库 → JSON 数据导出脚本
└── README.md
```

## 功能模块

### 仪表盘
- 📈 地图大小趋势图（主世界 / 下界 / 末地折线图）
- 👥 玩家统计图表（游戏时长、死亡次数、击杀怪物数量）
- 🔍 多玩家筛选与对比，支持全选/单选/多选

### 战斗统计
- ⚔️ 怪物击杀排行（按玩家筛选）
- 🛡️ 被怪物击杀排行
- 🏆 Top 10 怪物统计表（含怪物中文译名）

### 数据扫描（本地模式）
- 📂 单文件夹扫描：选择服务器备份文件夹 + 自定义日期
- 📁 批量导入：选择父文件夹，自动识别子文件夹中的日期并批量导入

### 数据管理（本地模式）
- 🗑️ 删除单日数据：Material You 风格下拉框选择日期
- 🧹 批量删除：Chips 风格多选组件，支持全选和逐个移除

## 快速开始

### 1. 初始化 UV 虚拟环境

```bash
uv init
uv add flask flask-cors
```

### 2. 启动本地服务器

```bash
uv run python mc_stats_server.py
```

访问 `http://localhost:5000` 即可使用全部功能（含数据扫描和数据管理）。

### 3. 导出数据并推送到 GitHub

```bash
uv run python scripts/export_data.py
git add data.json
git commit -m "更新数据"
git push origin main
```

### 4. 部署为静态页面（GitHub Pages）

在 GitHub 仓库 **Settings → Pages** 中启用 GitHub Pages（选择 main 分支）。

> 静态模式下，「数据扫描」和「数据管理」标签会自动隐藏，仅保留仪表盘和战斗统计。

## API 接口（本地模式）

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/map_sizes` | 获取地图大小数据 |
| GET | `/api/player_stats?type=` | 获取玩家统计（play_time / deaths / mob_kills） |
| GET | `/api/battle_stats?category=` | 获取战斗统计（killed / killed_by） |
| DELETE | `/api/delete_date` | 删除指定日期的所有数据 |
| DELETE | `/api/batch_delete` | 批量删除多个日期的数据 |

## 数据导出脚本

```bash
python scripts/export_data.py
```

从 `mc_stats.db` 读取数据并导出为 `data.json`，包含三个部分：

- `map_sizes` — 地图尺寸（主世界 / 下界 / 末地，单位 MB）
- `player_stats` — 玩家统计（游戏时长、死亡次数、击杀怪物数）
- `battle_stats` — 战斗统计（怪物击杀 / 被怪物击杀，按类别、日期、玩家、怪物层级组织）

## 技术栈

- **前端**：原生 HTML/CSS/JS + Chart.js + Google Material Icons
- **UI 风格**：Material You Design（圆角卡片、自适应主题色）
- **后端**：Python Flask + SQLite
- **部署**：支持 Flask 本地服务器 + GitHub Pages 静态托管双模式

## 开发说明

- 前端自动检测运行模式：`localhost:5000` 为本地服务器模式，否则为静态页面模式
- 本地模式下自动从 API 加载数据，静态模式下从 `data.json` 加载
- `.gitignore` 中排除了 `mc_stats_server.py`、`requirements.txt` 等本地开发文件