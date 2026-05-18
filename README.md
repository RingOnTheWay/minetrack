<div align="center">

# MineTrack - Minecraft 服务器数据统计

**Vue 3 + Flask 分层架构的 Minecraft 服务器数据统计面板**

[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.9+-blue?style=flat-square)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0+-lightgray?style=flat-square)](https://flask.palletsprojects.com/)
[![Vue](https://img.shields.io/badge/Vue-3.4+-4FC08D?style=flat-square)](https://vuejs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.4+-3178C6?style=flat-square)](https://www.typescriptlang.org/)
[![Vite](https://img.shields.io/badge/Vite-5.0+-646CFF?style=flat-square)](https://vitejs.dev/)
[![Pinia](https://img.shields.io/badge/Pinia-2.0+-FFD859?style=flat-square)](https://pinia.vuejs.org/)
[![ECharts](https://img.shields.io/badge/ECharts-6.0+-E43961?style=flat-square)](https://echarts.apache.org/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-4.0+-06B6D4?style=flat-square)](https://tailwindcss.com/)
[![Demo](https://img.shields.io/badge/Demo-Online-blue?style=flat-square)](https://ringontheway.github.io/minetrack/)

<img title="" src="frontend/public/icon.png" alt="MineTrack" align="center" height="96">

**中文 |** **[English](README-EN.md)**

⭐ 如果您喜欢这个项目，请在 GitHub 上给它一个 Star — 感谢支持！

[功能模块](#功能模块) • [快速开始](#快速开始) • [API 接口](#api-接口) • [技术栈](#技术栈) • [项目结构](#项目结构) • [前端路由](#前端路由)

</div>

***

## 概述

MineTrack 是一个 Vue 3 + Flask 分层架构的 Minecraft 服务器数据统计面板，支持本地数据扫描导入和静态页面部署两种模式。涵盖地图大小趋势、玩家统计、战斗统计、物品合成、物品拾取/丢弃/使用、方块统计、活动统计等全方位数据可视化。支持暗色模式、9 种主题色切换、中英文双语、时间范围筛选。

## 功能模块

### 仪表盘

- 📊 统计总览：统计天数、玩家数量、日期范围（带数字递增动画）
- 📈 快速导航到各统计页面（悬浮放大动效）
- 🗺️ 最新地图大小一览（带脉冲动画指示器）
- 📉 地图大小趋势折线图（含增长率）

### 地图统计

- 📈 地图大小趋势图（主世界 / 下界 / 末地折线图，带面积填充）
- 🔍 多玩家筛选与对比
- 📅 时间范围筛选
- 📊 增长率实时计算

### 玩家统计

- 👥 6 类核心指标：游戏时长(小时)、死亡次数、击杀怪物、击杀玩家、跳跃次数、行走距离(km)
- 📊 折线图展示，支持切换统计类型
- 🔍 多玩家筛选与对比（黄金角分布配色）
- 📅 时间范围筛选

### 战斗统计

- ⚔️ 怪物击杀排行（按玩家筛选）
- 🛡️ 被怪物击杀排行
- 🏆 Top 10 怪物统计表（含 76+ 种生物中英文名称翻译）
- 🥇 前三名奖牌样式高亮
- 📅 时间范围筛选

### 物品合成

- 🔨 物品合成统计（crafted / used 两类）
- 📊 按日期趋势的柱状图 + Top 10 物品排行
- 👤 支持多玩家筛选对比
- 🌐 含 740+ 种物品中英文名称翻译
- 📅 时间范围筛选

### 物品统计

- 📦 物品拾取 / 丢弃 / 使用统计（picked\_up / dropped / used）
- 📈 按日期趋势柱状图 + Top 10 排行
- 👤 支持多玩家筛选对比
- 📅 时间范围筛选

### 方块统计

- ⛏️ 方块挖掘与工具损耗统计（mined / broken 两类）
- 📊 按日期趋势柱状图 + Top 10 方块排行
- 👤 支持多玩家筛选对比
- 📅 时间范围筛选

### 活动统计

- 🏃‍♂️ 9 类活动数据：冲刺、走路、飞行、攀爬、游泳、骑马、乘船、鞘翅飞行、坠落
- 📊 按日期趋势的柱状图，支持切换活动类型查看
- 👤 支持多玩家筛选对比
- 📅 时间范围筛选

### 时间范围筛选

- 📅 所有统计页面支持按日期范围筛选图表数据
- 🗓️ 自定义日历弹窗：支持年/月/日三级导航，点击年份进入年选择、点击月份进入月选择
- 🚫 无数据日期自动禁用（日/月/年视图中均生效）
- 🔄 范围选择：先选开始日期再选结束日期，选完自动关闭；两个日期都选了再点从头开始
- 🧹 清除筛选按钮，支持弹窗内和输入框外清除
- 🔒 玩家筛选与时间筛选互斥，打开一个自动关闭另一个

### 数据管理（本地模式）

- 📂 单次扫描导入：输入路径或使用文件夹浏览器选择服务器文件夹
- 📁 批量扫描导入：自动从 `server.properties` 识别日期
- 🗂️ 文件夹浏览器：支持驱动器选择、目录逐级浏览、不可访问目录标记
- 🗑️ 按日期删除：自定义日历弹窗选择器（与统计页共享组件）
- 🧹 批量删除：日期范围选择器（与统计页共享组件）
- ⚠️ 删除全部数据（带确认弹窗）

### 玩家导入筛选

- 🔀 总开关：默认关闭，开启后导入数据时自动筛选玩家
- ⏱️ 最小游戏时长：游戏时长低于阈值的玩家将被过滤（默认 1 小时）
- ✅ 白名单：配置后仅导入白名单中的玩家，其他玩家一律排除
- ❌ 黑名单：黑名单中的玩家始终排除（与白名单互斥，添加一方自动移除另一方）
- 📊 扫描结果反馈：导入完成后显示过滤人数

### 个性化设置

- 🎨 9 种主题色预设（Emerald / Amber / Teal / Rose / Sky / HotPink / Gold / Navy / Crimson）
- 🌙 暗色模式（跟随系统偏好或手动切换）
- 🌐 中英文双语切换（语言偏好持久化到 localStorage）
- 📊 图表显示总计开关
- 👥 图例玩家数量：设置图表中最多显示的玩家数据线数量（默认 10）
- 🔀 玩家导入筛选：总开关、最小游戏时长、白名单、黑名单（详见上方「玩家导入筛选」）

## 快速开始

### 环境要求

- **Python** >= 3.9
- **Node.js** >= 18
- **uv** ([安装指南](https://docs.astral.sh/uv/getting-started/installation/))

### 方式一：一键启动（Windows）

双击 `start.bat` 即可自动检查依赖、启动前后端服务并打开浏览器。

### 方式二：手动启动

#### 1. 初始化后端

```bash
uv sync
```

#### 2. 启动后端服务器

```bash
uv run python backend/main.py
```

后端运行在 `http://localhost:5000`。

#### 3. 初始化并启动前端

```bash
cd frontend
npm install
npm run dev
```

前端运行在 `http://localhost:5173`，自动代理 API 请求到后端。

#### 4. 导出静态数据并部署 GitHub Pages

```bash
uv run python scripts/export_data.py
```

将 `frontend/dist/` 部署到 GitHub Pages 即可。

> 静态模式下，前端从 `data.json` 加载数据，「数据管理」功能不可用。

## API 接口

| 方法     | 路径                                            | 说明                                                                                         |
|:------ |:--------------------------------------------- |:------------------------------------------------------------------------------------------ |
| GET    | `/api/dates`                                  | 获取所有已记录日期列表                                                                                |
| GET    | `/api/map_sizes`                              | 获取地图大小数据                                                                                   |
| GET    | `/api/player_stats?type=`                     | 获取玩家统计（16 种 type，详见下方）                                                                     |
| GET    | `/api/stats/:domain?category=`                | 详细统计（domain: battle/craft/item/block）                                                      |
| GET    | `/api/stats/:domain/summary?category=&limit=` | 统计汇总 Top N（默认 limit=10）                                                                    |
| GET    | `/api/browse?path=`                           | 浏览目录（支持 Windows 驱动器枚举）                                                                     |
| POST   | `/api/scan`                                   | `{"folder":"..."}` 扫描单个文件夹                                                                 |
| POST   | `/api/batch_scan`                             | `{"parent_folder":"..."}` 批量扫描父文件夹                                                         |
| POST   | `/api/export`                                 | 导出数据为 JSON                                                                                 |
| DELETE | `/api/delete_date`                            | `{"date":"..."}` 删除指定日期数据                                                                  |
| DELETE | `/api/batch_delete`                           | `{"dates":["...","..."]}` 批量删除日期数据                                                         |
| DELETE | `/api/delete_all`                             | 清空所有数据                                                                                     |
| GET    | `/api/settings`                               | 获取所有设置（含 filter_enabled / min_playtime_hours / whitelist / blacklist / max_legend_players） |
| POST   | `/api/settings`                               | 更新设置（允许的键同上）                                                                               |

> 向后兼容：`/api/battle_stats`、`/api/craft_stats`、`/api/item_stats`、`/api/block_stats`、`/api/battle_summary`、`/api/block_summary` 仍可用，均映射至 `/api/stats/:domain` 统一接口。

**player\_stats 支持的 type 参数：** `play_time`, `deaths`, `mob_kills`, `player_kills`, `jumps`, `damage_dealt`, `distance_walked`, `sprint_one_cm`, `walk_one_cm`, `fly_one_cm`, `climb_one_cm`, `swim_one_cm`, `horse_one_cm`, `boat_one_cm`, `aviate_one_cm`, `fall_one_cm`

## 数据导出

```bash
uv run python scripts/export_data.py
```

从 `minetrack.db` 读取数据并导出为 `data.json`。

## 技术栈

| 组件     | 技术                                   |
|:------ |:------------------------------------:|
| 前端框架   | Vue 3 + TypeScript (Composition API) |
| 构建工具   | Vite 5                               |
| CSS 框架 | Tailwind CSS 4                       |
| 图表库    | ECharts 6 + vue-echarts              |
| 动画库    | @vueuse/motion                       |
| 图标库    | Lucide Icons                         |
| 国际化    | vue-i18n                             |
| 状态管理   | Pinia                                |
| 后端     | Python Flask 3 (分层架构)                |
| 数据库    | SQLite (WAL 模式)                      |
| 包管理    | uv (Python) + npm (Node.js)          |
| 部署     | Flask 本地服务器 / GitHub Pages           |

## 项目结构

```
stat/
├── frontend/                          # Vue 3 + Vite 前端
│   ├── src/
│   │   ├── main.ts                    # Vue 入口（含 localStorage 语言读取）
│   │   ├── App.vue                    # 根组件
│   │   ├── router/index.ts            # Vue Router 路由（Hash 模式）
│   │   ├── stores/
│   │   │   ├── app.ts                 # 全局状态（模式/暗色模式/主题色/图表设置/图例数量）
│   │   │   └── data.ts                # 统计数据状态管理（双模式加载）
│   │   ├── services/
│   │   │   ├── api.ts                 # API 调用层（自动切换本地/静态模式）
│   │   │   ├── usePlayerFilter.ts     # 玩家筛选 composable
│   │   │   └── useDateRange.ts        # 日期范围筛选 composable
│   │   ├── i18n/
│   │   │   ├── index.ts               # vue-i18n 配置
│   │   │   ├── zh-CN.json             # 中文翻译
│   │   │   ├── en-US.json             # 英文翻译
│   │   │   ├── mobs.ts                # 76+ 种生物中英文名称
│   │   │   └── items.ts               # 740+ 种物品中英文名称
│   │   ├── components/
│   │   │   ├── AppLayout.vue          # 布局容器
│   │   │   ├── Sidebar.vue            # 侧边栏导航（语言/暗色模式切换）
│   │   │   ├── TopBar.vue             # 顶部导航栏
│   │   │   ├── ChartContainer.vue     # ECharts 图表容器
│   │   │   ├── PlayerFilter.vue       # 玩家筛选组件
│   │   │   ├── DateRangeFilter.vue    # 日期范围筛选组件
│   │   │   └── DatePickerPopup.vue    # 共享日期选择弹窗组件
│   │   └── pages/
│   │       ├── DashboardPage.vue      # 仪表盘总览
│   │       ├── MapStatsPage.vue       # 地图统计
│   │       ├── PlayerStatsPage.vue    # 玩家统计
│   │       ├── BattleStatsPage.vue    # 战斗统计
│   │       ├── CraftStatsPage.vue     # 合成统计
│   │       ├── ItemStatsPage.vue      # 物品统计
│   │       ├── BlockStatsPage.vue     # 方块统计
│   │       ├── ActivityPage.vue       # 活动统计
│   │       ├── DataImportPage.vue     # 数据管理（导入/删除）
│   │       └── SettingsPage.vue       # 个性化设置
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
│   └── export_data.py                 # 数据导出脚本
├── assets/
│   └── icon.png
├── minetrack.db                       # SQLite 数据库
├── data.json                          # 静态导出数据
├── start.bat                          # Windows 一键启动脚本
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
minetrack.db      ← SQLite 数据库（WAL 模式）
```

### 前端状态管理

```
pages/            ← Vue 页面组件（按路由懒加载）
    ↓
components/       ← 可复用 UI 组件（ChartContainer / PlayerFilter / DateRangeFilter / DatePickerPopup）
    ↓
stores/           ← Pinia Store（app + data）
    ↓
services/         ← Composables（usePlayerFilter / useDateRange）+ API 调用层
```

## 前端路由

| 路径              | 页面组件            | 说明                              |
|:--------------- |:--------------- |:------------------------------- |
| `#/`            | DashboardPage   | 仪表盘总览                           |
| `#/map`         | MapStatsPage    | 地图大小趋势                          |
| `#/players`     | PlayerStatsPage | 6 类核心玩家数据统计                     |
| `#/battle`      | BattleStatsPage | 战斗击杀统计                          |
| `#/craft`       | CraftStatsPage  | 物品合成统计                          |
| `#/items`       | ItemStatsPage   | 物品拾取/丢弃/使用                      |
| `#/blocks`      | BlockStatsPage  | 方块挖掘与工具损耗统计                     |
| `#/activity`    | ActivityPage    | 9 类活动距离统计                       |
| `#/data-manage` | DataImportPage  | 数据导入与删除管理                       |
| `#/settings`    | SettingsPage    | 主题色 / 暗色模式 / 图表设置 / 玩家筛选 / 关于信息 |

> 使用 Hash 路由（`createWebHashHistory`）兼容 GitHub Pages 静态部署。

## 开发说明

- 前端通过 Vite proxy 将 `/api/*` 请求代理到 Flask 后端 `localhost:5000`
- 静态模式下前端读取根目录 `data.json`，API 请求失败时自动降级到静态模式
- 数据库使用 SQLite WAL 模式提升并发读写性能
- `detail_stats` 表通过 `stat_domain` 字段统一管理 battle / craft / item / block 四类统计，新增统计类型只需写入新 domain 即可
- 后端 `services/parser.py` 提供通用 `parse_detail_stats_by_domain()` 函数，接收 domain 和 categories 字典即可解析任意统计类型
- `services/scanner.py` 批量扫描时自动从文件夹名解析日期（支持 `YYYY-MM-DD`、`YYYY.MM.DD`、`YYYY_MM_DD`、`MM.DD` 等格式），三级降级策略：server.properties → 文件夹名 → 修改时间
- 主题色通过 CSS 自定义属性 `--color-brand` / `--brand` 实时切换，所有组件和图表均响应
- 语言偏好、暗色模式、主题色选择、图表显示总计、图例玩家数量均持久化到 localStorage
- 玩家导入筛选配置持久化到数据库 `settings` 表（key-value 结构），支持白名单/黑名单/最小时长三种筛选方式
- 白名单与黑名单互斥：添加到一方时自动从另一方移除；白名单不为空时仅导入白名单玩家
- 图例玩家数量设置控制图表中最多显示的 series 数量，默认 10
- ECharts tooltip 自定义 formatter：按数值降序排列，最多显示前 10 条数据，超出部分显示省略提示

## 特别鸣谢

- [ECharts](https://echarts.apache.org/) - 强大的开源可视化图表库
- [Vue.js](https://vuejs.org/) - 渐进式 JavaScript 框架
- [Flask](https://flask.palletsprojects.com/) - Python 微框架
- [Tailwind CSS](https://tailwindcss.com/) - 实用优先的 CSS 框架
- [Lucide](https://lucide.dev/) - 精美的开源图标库

## 许可证

本项目采用 [MIT](https://opensource.org/licenses/MIT) 许可证。
