<div align="center">

# MC Stats - Minecraft 服务器数据统计

**Vue 3 + Flask 分层架构的 Minecraft 服务器数据统计面板**

[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.9+-blue?style=flat-square)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0+-lightgray?style=flat-square)](https://flask.palletsprojects.com/)
[![Vue](https://img.shields.io/badge/Vue-3.4+-4FC08D?style=flat-square)](https://vuejs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-3178C6?style=flat-square)](https://www.typescriptlang.org/)
[![Vite](https://img.shields.io/badge/Vite-5.0+-646CFF?style=flat-square)](https://vitejs.dev/)
[![Pinia](https://img.shields.io/badge/Pinia-2.0+-FFD859?style=flat-square)](https://pinia.vuejs.org/)
[![Chart.js](https://img.shields.io/badge/Chart.js-4.0+-orange?style=flat-square)](https://www.chartjs.org/)
[![Demo](https://img.shields.io/badge/Demo-Online-blue?style=flat-square)](https://ringontheway.github.io/mc-stats/)

<img src="assets/icon.png" alt="MC Stats" align="center" height="96" />

**中文 | [English](README-EN.md)**

⭐ 如果您喜欢这个项目，请在 GitHub 上给它一个 Star — 感谢支持！

[功能模块](#功能模块) • [快速开始](#快速开始) • [API 接口](#api-接口) • [技术栈](#技术栈) • [项目结构](#项目结构) • [前端路由](#前端路由)

</div>

***

## 概述

MC Stats 是一个 Vue 3 + Flask 分层架构的 Minecraft 服务器数据统计面板，支持本地数据扫描导入和静态页面部署两种模式。涵盖地图大小趋势、玩家统计、战斗统计、物品合成、物品拾取/丢弃/使用、活动统计等全方位数据可视化。

## 功能模块

### 仪表盘
- 📊 统计总览：统计天数、玩家数量、日期范围
- 📈 快速导航到各统计页面
- 🗺️ 最新地图大小一览

### 地图统计
- 📈 地图大小趋势图（主世界 / 下界 / 末地折线图）
- 🔍 多玩家筛选与对比

### 玩家统计
- 👥 16 类玩家数据：游戏时长、死亡次数、击杀怪物/玩家、跳跃、造成伤害及其他活动距离
- 📊 折线图展示，支持切换统计类型
- 🔍 多玩家筛选与对比

### 战斗统计
- ⚔️ 怪物击杀排行（按玩家筛选）
- 🛡️ 被怪物击杀排行
- 🏆 Top 10 怪物统计表（含怪物中文译名）

### 物品合成
- 🔨 物品合成统计（crafted / used 两类）
- 📊 按日期趋势的条形图 + Top 10 物品排行
- 👤 支持多玩家筛选对比

### 物品统计
- 📦 物品拾取 / 丢弃 / 使用统计（picked_up / dropped / used）
- 📈 按日期趋势图表 + Top 10 排行
- 👤 支持多玩家筛选对比

### 活动统计
- 🏃‍♂️ 9 类活动数据：冲刺、走路、飞行、攀爬、游泳、骑马、乘船、鞘翅飞行、坠落
- 📊 按日期趋势的条形图，支持切换活动类型查看
- 👤 支持多玩家筛选对比

### 数据扫描（本地模式）
- 📂 单文件夹扫描：选择服务器备份文件夹 + 自定义日期
- 📁 批量导入：选择父文件夹，自动识别子文件夹中的日期并批量导入

### 数据管理（本地模式）
- 🗑️ 删除单日数据
- 🧹 批量删除多个日期的数据

## 快速开始

### 环境要求

- **Python** >= 3.9
- **Node.js** >= 18
- **uv** ([安装指南](https://docs.astral.sh/uv/getting-started/installation/))

### 1. 初始化后端

```bash
uv sync
```

### 2. 启动后端服务器

```bash
uv run python backend/main.py
```

后端运行在 `http://localhost:5000`。

### 3. 初始化并启动前端

```bash
cd frontend
npm install
npm run dev
```

前端运行在 `http://localhost:5173`，自动代理 API 请求到后端。

### 4. 导出静态数据并部署 GitHub Pages

```bash
uv run python scripts/export_data.py
```

将 `frontend/dist/` 部署到 GitHub Pages 即可。

> 静态模式下，前端从 `data.json` 加载数据，「数据扫描」和「数据管理」功能不可用。

## API 接口

| 方法 | 路径 | 说明 |
|:-----|:-----|:-----|
| GET | `/api/dates` | 获取所有已记录日期列表 |
| GET | `/api/map_sizes` | 获取地图大小数据 |
| GET | `/api/player_stats?type=` | 获取玩家统计（16 种 type，详见下方） |
| GET | `/api/stats/:domain?category=` | 详细统计（domain: battle/craft/item） |
| GET | `/api/stats/:domain/summary?category=&limit=` | 统计汇总 Top N（默认 limit=10） |
| POST | `/api/scan` | `{"folder":"...", "date":"..."}` 扫描单个文件夹 |
| POST | `/api/batch_scan` | `{"parent_folder":"..."}` 批量扫描父文件夹 |
| POST | `/api/export` | 导出数据为 JSON |
| DELETE | `/api/delete_date` | `{"date":"..."}` 删除指定日期数据 |
| DELETE | `/api/batch_delete` | `{"dates":["...","..."]}` 批量删除日期数据 |

> 向后兼容：`/api/battle_stats`、`/api/craft_stats`、`/api/item_stats`、`/api/battle_summary` 仍可用，均映射至 `/api/stats/:domain` 统一接口。

**player_stats 支持的 type 参数：** `play_time`, `deaths`, `mob_kills`, `player_kills`, `jumps`, `damage_dealt`, `distance_walked`, `sprint_one_cm`, `walk_one_cm`, `fly_one_cm`, `climb_one_cm`, `swim_one_cm`, `horse_one_cm`, `boat_one_cm`, `aviate_one_cm`, `fall_one_cm`

## 数据导出

```bash
uv run python scripts/export_data.py
```

从 `mc_stats.db` 读取数据并导出为 `data.json`。

## 数据迁移（旧架构升级）

如果是从旧版本（`mc_stats_server.py` 单体架构）升级：

```bash
uv run python scripts/migrate_db.py
```

此脚本将旧的 `battle_stats` / `craft_stats` / `item_stats` 三表合并为 `detail_stats` 统一表。

## 技术栈

| 组件 | 技术 |
|:-----|:----:|
| 前端框架 | Vue 3 + TypeScript (Composition API) |
| 构建工具 | Vite 5 |
| 图表库 | Chart.js 4 + vue-chartjs |
| 国际化 | vue-i18n |
| 状态管理 | Pinia |
| UI 风格 | Material You Design |
| 后端 | Python Flask 3 (分层架构) |
| 数据库 | SQLite (WAL 模式) |
| 包管理 | uv (Python) + npm (Node.js) |
| 部署 | Flask 本地服务器 / GitHub Pages |

## 项目结构

```
stat/
├── frontend/                          # Vue 3 + Vite 前端
│   ├── src/
│   │   ├── main.ts                    # Vue 入口
│   │   ├── App.vue                    # 根组件
│   │   ├── router/index.ts            # Vue Router 路由
│   │   ├── stores/
│   │   │   ├── app.ts                 # 全局状态（模式/加载）
│   │   │   └── data.ts                # 统计数据状态管理
│   │   ├── services/
│   │   │   ├── api.ts                 # API 调用层
│   │   │   └── usePlayerFilter.ts     # 玩家筛选 composable
│   │   ├── i18n/
│   │   │   ├── index.ts               # vue-i18n 配置
│   │   │   ├── zh-CN.json             # 中文翻译
│   │   │   └── en-US.json             # 英文翻译
│   │   ├── components/
│   │   │   ├── AppLayout.vue          # 布局容器
│   │   │   ├── Sidebar.vue            # 侧边栏导航
│   │   │   ├── TopBar.vue             # 顶部导航栏
│   │   │   └── PlayerFilter.vue       # 玩家筛选组件
│   │   └── pages/
│   │       ├── DashboardPage.vue      # 仪表盘总览
│   │       ├── MapStatsPage.vue       # 地图统计
│   │       ├── PlayerStatsPage.vue    # 玩家统计
│   │       ├── BattleStatsPage.vue    # 战斗统计
│   │       ├── CraftStatsPage.vue     # 合成统计
│   │       ├── ItemStatsPage.vue      # 物品统计
│   │       └── ActivityPage.vue       # 活动统计
│   ├── public/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.ts
│   └── tsconfig.json
│
├── backend/                           # Flask 分层后端
│   ├── app.py                         # Flask 应用工厂
│   ├── config.py                      # 配置管理
│   ├── main.py                        # 入口点
│   ├── database/
│   │   ├── __init__.py
│   │   ├── init.py                    # 数据库初始化 + Schema
│   │   └── repositories.py           # Repository 数据访问层
│   ├── services/
│   │   ├── parser.py                  # 通用 Stats 解析器
│   │   ├── scanner.py                 # 服务器文件夹扫描
│   │   └── exporter.py               # 数据导出服务
│   └── routes/
│       └── api.py                     # 所有 API Blueprint
│
├── locales/                           # 独立翻译文件（静态模式）
│   ├── zh-CN.json
│   └── en-US.json
├── scripts/
│   ├── export_data.py                 # 数据导出脚本
│   └── migrate_db.py                 # 数据迁移脚本
├── assets/
│   └── icon.png
├── mc_stats.db                        # SQLite 数据库
├── data.json                          # 静态导出数据
├── pyproject.toml                     # UV 项目配置
├── .gitignore
├── README.md
└── README-EN.md
```

## 架构设计

### 后端分层

```
routes/api.py     ← HTTP 请求处理（Flask Blueprint）
    ↓
services/         ← 业务逻辑（解析 / 扫描 / 导出）
    ↓
database/         ← Repository 模式数据访问层
    ↓
mc_stats.db       ← SQLite 数据库（WAL 模式）
```

### 前端状态管理

```
pages/            ← Vue 页面组件（按路由懒加载）
    ↓
components/       ← 可复用 UI 组件
    ↓
stores/           ← Pinia Store（app + data）
    ↓
services/api.ts   ← 统一 API 调用（自动切换本地/静态模式）
```

## 前端路由

| 路径 | 页面组件 | 说明 |
|:-----|:---------|:-----|
| `#/` | DashboardPage | 仪表盘总览 |
| `#/map` | MapStatsPage | 地图大小趋势 |
| `#/players` | PlayerStatsPage | 16 类玩家数据统计 |
| `#/battle` | BattleStatsPage | 战斗击杀统计 |
| `#/craft` | CraftStatsPage | 物品合成统计 |
| `#/items` | ItemStatsPage | 物品拾取/丢弃/使用 |
| `#/activity` | ActivityPage | 9 类活动距离统计 |

> 使用 Hash 路由（`createWebHashHistory`）兼容 GitHub Pages 静态部署。

## 开发说明

- 前端通过 Vite proxy 将 `/api/*` 请求代理到 Flask 后端 `localhost:5000`
- 静态模式下前端读取根目录 `data.json`，构建时放入 `frontend/public/` 一并打包
- 数据库使用 SQLite WAL 模式提升并发读写性能
- `detail_stats` 表通过 `stat_domain` 字段统一管理 battle / craft / item 三类统计，新增统计类型只需写入新 domain 即可
- 后端 `services/parser.py` 提供通用 `parse_detail_stats_by_domain()` 函数，接收 domain 和 categories 字典即可解析任意统计类型
- `services/scanner.py` 批量扫描时自动从文件夹名解析日期（支持 `YYYY-MM-DD`、`YYYY.MM.DD`、`MM.DD` 等格式）
- `scripts/migrate_db.py` 将旧版三表（battle_stats / craft_stats / item_stats）合并为 detail_stats，执行后删除旧表

## 特别鸣谢

- [Chart.js](https://www.chartjs.org/) - 强大的开源图表库
- [Vue.js](https://vuejs.org/) - 渐进式 JavaScript 框架
- [Flask](https://flask.palletsprojects.com/) - Python 微框架

## 许可证

本项目采用 [MIT](https://opensource.org/licenses/MIT) 许可证。