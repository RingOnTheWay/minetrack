<div align="center">

# MineTrack - Minecraft Server Data Statistics

**Vue 3 + Flask layered architecture Minecraft server data statistics panel**

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

**[简体中文](README.md)** **| English**

⭐ If you like this project, please give it a Star on GitHub — Thank you!

[Features](#features) • [Quick Start](#quick-start) • [API Endpoints](#api-endpoints) • [Tech Stack](#tech-stack) • [Project Structure](#project-structure) • [Frontend Routes](#frontend-routes)

</div>

***

## Overview

MineTrack is a Minecraft server data statistics panel built with Vue 3 + Flask layered architecture, supporting two modes: local data scanning import and static page deployment. It covers comprehensive data visualization including map size trends, player statistics, battle statistics, item crafting, item pickups/drops/usage, block statistics, and player activity statistics.

## Features

### Dashboard

- 📊 Overview: total days, player count, date range (with number counting animation)
- 📈 Quick navigation to all statistics pages (with hover scale animation)
- 🗺️ Latest map sizes at a glance (with pulse animation indicators)
- 📉 Map size trend line chart (with growth rate)

### Map Statistics

- 📈 Map size trends (Overworld / Nether / End line charts with area fill)
- 🔍 Multi-player filtering and comparison
- 📅 Time range filtering
- 📊 Real-time growth rate calculation

### Player Statistics

- 👥 6 core metrics: play time (hours), deaths, mob kills, player kills, jumps, walk distance (km)
- 📊 Line charts with stat type switching
- 🔍 Multi-player filtering and comparison (golden angle distribution colors)
- 📅 Time range filtering

### Battle Statistics

- ⚔️ Mob kill ranking (filtered by player)
- 🛡️ Killed by mob ranking
- 🏆 Top 10 mob statistics (with 76+ mob name translations)
- 🥇 Medal-style highlighting for top 3
- 📅 Time range filtering

### Item Crafting

- 🔨 Crafting statistics (crafted / used categories)
- 📊 Date trend bar chart + Top 10 items ranking
- 👤 Multi-player filtering support
- 🌐 740+ item name translations
- 📅 Time range filtering

### Item Statistics

- 📦 Item pickups / drops / usage (picked\_up / dropped / used)
- 📈 Date trend bar chart + Top 10 ranking
- 👤 Multi-player filtering support
- 📅 Time range filtering

### Block Statistics

- ⛏️ Block mining and tool wear statistics (mined / broken categories)
- 📊 Date trend bar chart + Top 10 blocks ranking
- 👤 Multi-player filtering support
- 📅 Time range filtering

### Activity Statistics

- 🏃‍♂️ 9 activity types: sprint, walk, fly, climb, swim, horse, boat, elytra, fall
- 📊 Date trend bar chart with activity type switching
- 👤 Multi-player filtering support
- 📅 Time range filtering

### Time Range Filtering

- 📅 All statistics pages support filtering chart data by date range
- 🗓️ Custom calendar popup: year/month/day three-level navigation, click year to enter year selection, click month to enter month selection
- 🚫 Dates without data are automatically disabled (applies in day/month/year views)
- 🔄 Range selection: select start date first, then end date; auto-closes when complete; clicking again after both dates resets from the beginning
- 

### Data Management (Local Mode)

- 📂 Single scan import: enter path or use folder browser to select server folder
- 🗜️ Archive scan import: supports zip / tar / 7z / rar formats with auto date detection
- 📁 Batch scan import: auto-detect dates from `server.properties`, with SSE streaming progress
- 🗂️ Folder browser: drive selection, directory navigation, inaccessible directory markers, archive file display
- 📋 Scannable items list: preview all scannable subfolders and archives under a parent folder
- 🗑️ Delete by date: custom calendar popup selector (shared component with statistics pages)
- 🧹 Batch delete: date range selector (shared component with statistics pages), with SSE streaming progress
- ⚠️ Delete all data (with confirmation dialog)

### Auto Scan (Local Mode)

- ⏰ APScheduler scheduled scan: auto-scan specified server folder daily at midnight
- 🔧 Auto scan config: enable/disable toggle + scan folder path
- 🚀 Manual trigger: trigger a one-time auto scan via API
- 📊 Scan status feedback: last scan time, success status, scan result

### Player Import Filter

- 🔀 Master switch: disabled by default; when enabled, players are automatically filtered during data import
- ⏱️ Minimum playtime: players below the threshold are filtered out (default 1 hour)
- ✅ Whitelist: when configured, only whitelisted players are imported; all others are excluded
- ❌ Blacklist: blacklisted players are always excluded (mutually exclusive with whitelist; adding to one auto-removes from the other)
- 📊 Scan result feedback: filtered player count shown after import

### Personalization Settings

- 🎨 9 theme color presets (Emerald / Amber / Teal / Rose / Sky / HotPink / Gold / Navy / Crimson)
- 🌙 Dark mode (follows system preference or manual toggle)
- 🌐 Bilingual switching (language preference persisted to localStorage)
- 📊 Chart total display toggle
- 👥 Legend player count: set the maximum number of player data lines shown in charts (default 10)
- 🔀 Player import filter: master switch, minimum playtime, whitelist, blacklist (see "Player Import Filter" above)

## Quick Start

### Requirements

- **Python** >= 3.9
- **Node.js** >= 18
- **uv** ([Installation Guide](https://docs.astral.sh/uv/getting-started/installation/))

### Option 1: One-Click Start (Windows)

Double-click `start.bat` to automatically check dependencies, start backend and frontend servers, and open the browser.

### Option 2: Manual Start

#### 1. Initialize Backend

```bash
uv sync
```

#### 2. Start Backend Server

```bash
uv run python backend/main.py
```

Backend runs at `http://localhost:5000`.

#### 3. Initialize and Start Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at `http://localhost:5173`, automatically proxying API requests to the backend.

#### 4. Export Static Data for GitHub Pages

```bash
uv run python scripts/export_data.py
```

Deploy `frontend/dist/` to GitHub Pages.

> In static mode, the frontend loads data from `data.json`. Data management features are not available.

## API Endpoints

| Method | Path                                          | Description                                                                     |
|:------ |:--------------------------------------------- |:------------------------------------------------------------------------------- |
| GET    | `/api/dates`                                  | Get all recorded dates                                                          |
| GET    | `/api/map_sizes`                              | Get map size data                                                               |
| GET    | `/api/player_stats?type=`                     | Get player stats (31 types, see below)                                          |
| GET    | `/api/stats/:domain?category=`                | Detail stats (domain: battle/craft/item/block)                                  |
| GET    | `/api/stats/:domain/summary?category=&limit=` | Stats summary Top N (default limit=10)                                          |
| GET    | `/api/browse?path=`                           | Browse directories (Windows drive enumeration, returns folders and archives)    |
| POST   | `/api/scan`                                   | `{"folder":"..."}` Scan a single folder                                         |
| POST   | `/api/scan_archive`                           | `{"archive":"..."}` Scan an archive (zip/tar/7z/rar)                            |
| POST   | `/api/batch_scan`                             | `{"parent_folder":"..."}` Batch scan parent folder                              |
| POST   | `/api/batch_scan_stream`                      | `{"parent_folder":"..."}` SSE streaming batch scan (mixed folders and archives) |
| POST   | `/api/list_scannable`                         | `{"parent_folder":"..."}` List scannable subfolders and archives                |
| POST   | `/api/export`                                 | Export data to JSON                                                             |
| DELETE | `/api/delete_date`                            | `{"date":"..."}` Delete data for a date                                         |
| DELETE | `/api/batch_delete`                           | `{"dates":["...","..."]}` Batch delete dates                                    |
| DELETE | `/api/batch_delete_stream`                    | `{"dates":["...","..."]}` SSE streaming batch delete                            |
| DELETE | `/api/delete_all`                             | Delete all data                                                                 |
| GET    | `/api/auto_scan/config`                       | Get auto scan config and last scan status                                       |
| POST   | `/api/auto_scan/config`                       | Update auto scan config (enabled / folder)                                      |
| POST   | `/api/auto_scan/trigger`                      | Manually trigger a one-time auto scan                                           |

> Backward compatible: `/api/battle_stats`, `/api/craft_stats`, `/api/item_stats`, `/api/block_stats`, `/api/battle_summary`, `/api/block_summary` are still available, all mapped to the unified `/api/stats/:domain` interface.

**player\_stats supported type values:** `play_time`, `deaths`, `mob_kills`, `player_kills`, `jumps`, `damage_dealt`, `damage_taken`, `distance_walked`, `sprint_one_cm`, `walk_one_cm`, `fly_one_cm`, `climb_one_cm`, `swim_one_cm`, `horse_one_cm`, `boat_one_cm`, `aviate_one_cm`, `fall_one_cm`, `sleep_in_bed`, `fish_caught`, `animals_bred`, `traded_with_villager`, `talked_to_villager`, `enchant_item`, `interact_with_crafting_table`, `interact_with_furnace`, `interact_with_anvil`, `open_chest`, `bell_ring`, `drop_count`, `eat_cake_slice`, `sneak_time`, `leave_game`

## Auto Import on Server Stop

Automatically trigger data import when the Minecraft server stops.

### Configuration

Add the following code snippets to your server's `run.bat`:

**1. Config variables** (paste after `@echo off`)

```bat
REM === MineTrack Auto Import Config ===
set MINETRACK_FOLDER=your_minetrack_folder
REM === End Config ===
```

> Change `MINETRACK_FOLDER` to your actual MineTrack project path.

**2. Auto import call** (paste after `echo Server stopped.`, before `choice`)

```bat
REM === MineTrack Auto Import ===
echo [MineTrack] Importing data...
cd /d "%MINETRACK_FOLDER%"
uv run python scripts/auto_import.py "%~dp0."
cd /d "%~dp0"
REM === End MineTrack Auto Import ===
```

### Full Example

```bat
@echo off
REM === MineTrack Auto Import Config ===
set MINETRACK_FOLDER=D:\Downloads\Server\Backup\stat
REM === End Config ===

:start
echo Starting Minecraft server...
java.exe -Xms2G -Xmx4G -jar purpur-26.1.2-2575.jar nogui

echo.
echo Server stopped.
REM === MineTrack Auto Import ===
echo [MineTrack] Importing data...
cd /d "%MINETRACK_FOLDER%"
uv run python scripts/auto_import.py "%~dp0."
cd /d "%~dp0"
REM === End MineTrack Auto Import ===

choice /C RN /M "Press R to restart, N to exit"
if errorlevel 2 goto exit
if errorlevel 1 goto start

:exit
echo Exiting...
```

### How It Works

1. Data import is automatically triggered when the server stops
2. The import date defaults to the current date at server stop time
3. Tries API import first (requires MineTrack backend running), falls back to direct Python call on failure
4. Does not modify any files in the server folder

### Manual Command Line

```bash
uv run python scripts/auto_import.py <server_folder> [date]
```

- `server_folder`: Path to the server folder
- `date`: Optional, import date (YYYY-MM-DD). Defaults to current date if omitted

## Data Export

```bash
uv run python scripts/export_data.py
```

Reads from `minetrack.db` and exports to `data.json`.

## Tech Stack

| Component            | Technology                            |
|:-------------------- |:-------------------------------------:|
| Frontend Framework   | Vue 3 + TypeScript (Composition API)  |
| Build Tool           | Vite 5                                |
| CSS Framework        | Tailwind CSS 4                        |
| Chart Library        | ECharts 6 + vue-echarts               |
| Animation Library    | @vueuse/motion                        |
| Icon Library         | Lucide Icons                          |
| Internationalization | vue-i18n                              |
| State Management     | Pinia                                 |
| Backend              | Python Flask 3 (Layered Architecture) |
| Database             | SQLite (WAL Mode)                     |
| Package Manager      | uv (Python) + npm (Node.js)           |
| Deployment           | Flask local server / GitHub Pages     |

## Project Structure

```
stat/
├── frontend/                          # Vue 3 + Vite Frontend
│   ├── src/
│   │   ├── main.ts                    # Vue entry point (with localStorage locale)
│   │   ├── App.vue                    # Root component
│   │   ├── router/index.ts            # Vue Router (Hash mode)
│   │   ├── stores/
│   │   │   ├── app.ts                 # Global state (mode/dark mode/theme color/chart settings/legend count)
│   │   │   └── data.ts                # Statistics data state (dual-mode loading)
│   │   ├── services/
│   │   │   ├── api.ts                 # API call layer (auto-switch local/static mode)
│   │   │   ├── usePlayerFilter.ts     # Player filter composable
│   │   │   └── useDateRange.ts        # Date range filter composable
│   │   ├── i18n/
│   │   │   ├── index.ts               # vue-i18n configuration
│   │   │   ├── zh-CN.json             # Chinese translations
│   │   │   ├── en-US.json             # English translations
│   │   │   ├── mobs.ts                # 76+ mob name translations
│   │   │   └── items.ts               # 740+ item name translations
│   │   ├── components/
│   │   │   ├── AppLayout.vue          # Layout container
│   │   │   ├── Sidebar.vue            # Sidebar navigation (locale/dark mode toggle)
│   │   │   ├── TopBar.vue             # Top navigation bar
│   │   │   ├── ChartContainer.vue     # ECharts chart container
│   │   │   ├── PlayerFilter.vue       # Player filter component
│   │   │   ├── DateRangeFilter.vue    # Date range filter component
│   │   │   └── DatePickerPopup.vue    # Shared date picker popup component
│   │   └── pages/
│   │       ├── DashboardPage.vue      # Dashboard overview
│   │       ├── MapStatsPage.vue       # Map statistics
│   │       ├── PlayerStatsPage.vue    # Player statistics
│   │       ├── BattleStatsPage.vue    # Battle statistics
│   │       ├── CraftStatsPage.vue     # Crafting statistics
│   │       ├── ItemStatsPage.vue      # Item statistics
│   │       ├── BlockStatsPage.vue     # Block statistics
│   │       ├── ActivityPage.vue       # Activity statistics
│   │       ├── DataImportPage.vue     # Data management (import/delete)
│   │       └── SettingsPage.vue       # Personalization settings
│   ├── public/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.ts
│   └── tsconfig.json
│
├── backend/                           # Flask Layered Backend
│   ├── app.py                         # Flask app factory
│   ├── config.py                      # Configuration management
│   ├── main.py                        # Entry point
│   ├── database/
│   │   ├── __init__.py
│   │   ├── init.py                    # Database initialization + Schema
│   │   └── repositories.py           # Repository data access layer
│   ├── services/
│   │   ├── parser.py                  # Universal stats parser
│   │   ├── scanner.py                 # Server folder scanner
│   │   ├── archiver.py                # Archive reader (zip/tar/7z/rar)
│   │   ├── scheduler.py               # APScheduler auto scan scheduler
│   │   └── exporter.py               # Data export service
│   └── routes/
│       └── api.py                     # All API Blueprint routes
│
├── locales/                           # Standalone translation files (static mode)
│   ├── zh-CN.json
│   └── en-US.json
├── scripts/
│   ├── auto_import.py               # Auto import script on server stop
│   └── export_data.py               # Data export script
├── assets/
│   └── icon.png
├── minetrack.db                       # SQLite database
├── data.json                          # Exported static data
├── start.bat                          # Windows one-click start script
├── pyproject.toml                     # UV project configuration
├── .gitignore
├── README.md
└── README-EN.md
```

## Architecture Design

### Backend Layers

```
routes/api.py     ← HTTP request handling (Flask Blueprint)
    ↓
services/         ← Business logic (parsing / scanning / archive reading / scheduling / exporting)
    ↓
database/         ← Repository pattern data access layer
    ↓
minetrack.db      ← SQLite database (WAL mode)
```

### Frontend State Management

```
pages/            ← Vue page components (lazy-loaded by route)
    ↓
components/       ← Reusable UI components (ChartContainer / PlayerFilter / DateRangeFilter / DatePickerPopup)
    ↓
stores/           ← Pinia Stores (app + data)
    ↓
services/         ← Composables (usePlayerFilter / useDateRange) + API call layer
```

## Frontend Routes

| Path            | Page Component  | Description                                                      |
|:--------------- |:--------------- |:---------------------------------------------------------------- |
| `#/`            | DashboardPage   | Dashboard overview                                               |
| `#/map`         | MapStatsPage    | Map size trends                                                  |
| `#/players`     | PlayerStatsPage | 6 core player data categories                                    |
| `#/battle`      | BattleStatsPage | Battle kill statistics                                           |
| `#/craft`       | CraftStatsPage  | Item crafting statistics                                         |
| `#/items`       | ItemStatsPage   | Pickup/drop/use statistics                                       |
| `#/blocks`      | BlockStatsPage  | Block mining and tool wear statistics                            |
| `#/activity`    | ActivityPage    | 9 activity distance statistics                                   |
| `#/data-manage` | DataImportPage  | Data import and delete management                                |
| `#/settings`    | SettingsPage    | Theme color / dark mode / chart settings / player filter / about |

> Uses Hash router (`createWebHashHistory`) for GitHub Pages static deployment compatibility.

## Development Notes

- The frontend proxies `/api/*` requests to the Flask backend at `localhost:5000` via Vite proxy
- In static mode, the frontend reads `data.json` from root; API request failures auto-fallback to static mode
- The database uses SQLite WAL mode for improved concurrent read/write performance, with 3 tables: `map_sizes`, `player_stats`, `detail_stats`
- The `detail_stats` table unifies battle/craft/item/block statistics via the `stat_domain` field; adding a new stat type only requires writing data with a new domain
- The backend `services/parser.py` provides a generic `parse_detail_stats_by_domain()` function that accepts a domain and categories dict to parse any stat type
- `services/scanner.py` batch scanning auto-detects dates from folder names (supports `YYYY-MM-DD`, `YYYY.MM.DD`, `YYYY_MM_DD`, `MM.DD` formats), with three-level fallback: server.properties → folder name → modification time
- `services/archiver.py` provides the `ArchiveReader` class supporting zip / tar / 7z / rar archive formats, using generator pattern for file-by-file reading with auto path prefix detection
- `services/scheduler.py` uses APScheduler for scheduled auto scanning (daily at midnight), config stored in memory and needs reconfiguration after backend restart
- Batch scan (`/api/batch_scan_stream`) and batch delete (`/api/batch_delete_stream`) use Server-Sent Events (SSE) for real-time progress updates
- Theme colors switch in real-time via CSS custom properties `--color-brand` / `--brand`, all components and charts respond
- Language preference, dark mode, theme color selection, chart total display, legend player count, and player import filter settings are persisted to localStorage
- Auto scan config (enabled state, scan folder) is stored in backend memory via API, with frontend caching to localStorage
- Whitelist and blacklist are mutually exclusive: adding to one auto-removes from the other; when whitelist is not empty, only whitelisted players are imported
- Legend player count setting controls the maximum number of series displayed in charts (default 10)
- ECharts tooltip custom formatter: sorted by value descending, shows top 10 items with overflow indicator

## Acknowledgments

- [ECharts](https://echarts.apache.org/) - Powerful open-source visualization library
- [Vue.js](https://vuejs.org/) - The Progressive JavaScript Framework
- [Flask](https://flask.palletsprojects.com/) - Python micro framework
- [Tailwind CSS](https://tailwindcss.com/) - Utility-first CSS framework
- [Lucide](https://lucide.dev/) - Beautiful open-source icon library

## License

This project is licensed under the [MIT](https://opensource.org/licenses/MIT) license.
