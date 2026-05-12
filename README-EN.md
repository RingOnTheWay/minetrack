<div align="center">

# MC Stats - Minecraft Server Data Statistics

**Vue 3 + Flask layered architecture Minecraft server data statistics panel**

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

**[简体中文](README.md) | English**

⭐ If you like this project, please give it a Star on GitHub — Thank you!

[Features](#features) • [Quick Start](#quick-start) • [API Endpoints](#api-endpoints) • [Tech Stack](#tech-stack) • [Project Structure](#project-structure) • [Frontend Routes](#frontend-routes)

</div>

***

## Overview

MC Stats is a Minecraft server data statistics panel built with Vue 3 + Flask layered architecture, supporting two modes: local data scanning import and static page deployment. It covers comprehensive data visualization including map size trends, player statistics, battle statistics, item crafting, item pickups/drops/usage, and player activity statistics.

## Features

### Dashboard
- 📊 Overview: total days, player count, date range
- 📈 Quick navigation to all statistics pages
- 🗺️ Latest map sizes at a glance

### Map Statistics
- 📈 Map size trends (Overworld / Nether / End line charts)
- 🔍 Multi-player filtering and comparison

### Player Statistics
- 👥 16 data categories: play time, deaths, mob/player kills, jumps, damage dealt, and movement distances
- 📊 Line charts with stat type switching
- 🔍 Multi-player filtering and comparison

### Battle Statistics
- ⚔️ Mob kill ranking (filtered by player)
- 🛡️ Killed by mob ranking
- 🏆 Top 10 mob statistics (with Chinese translations)

### Item Crafting
- 🔨 Crafting statistics (crafted / used categories)
- 📊 Date trend bar chart + Top 10 items ranking
- 👤 Multi-player filtering support

### Item Statistics
- 📦 Item pickups / drops / usage (picked_up / dropped / used)
- 📈 Date trend chart + Top 10 ranking
- 👤 Multi-player filtering support

### Activity Statistics
- 🏃‍♂️ 9 activity types: sprint, walk, fly, climb, swim, horse, boat, elytra, fall
- 📊 Date trend bar chart with activity type switching
- 👤 Multi-player filtering support

### Data Scanning (Local Mode)
- 📂 Single folder scan: select server backup folder + custom date
- 📁 Batch import: select parent folder, auto-detect dates in subfolders

### Data Management (Local Mode)
- 🗑️ Delete single day data
- 🧹 Batch delete data for multiple dates

## Quick Start

### Requirements

- **Python** >= 3.9
- **Node.js** >= 18
- **uv** ([Installation Guide](https://docs.astral.sh/uv/getting-started/installation/))

### 1. Initialize Backend

```bash
uv sync
```

### 2. Start Backend Server

```bash
uv run python backend/main.py
```

Backend runs at `http://localhost:5000`.

### 3. Initialize and Start Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at `http://localhost:5173`, automatically proxying API requests to the backend.

### 4. Export Static Data for GitHub Pages

```bash
uv run python scripts/export_data.py
```

Deploy `frontend/dist/` to GitHub Pages.

> In static mode, the frontend loads data from `data.json`. Data scanning and management features are not available.

## API Endpoints

| Method | Path | Description |
|:-------|:-----|:------------|
| GET | `/api/dates` | Get all recorded dates |
| GET | `/api/map_sizes` | Get map size data |
| GET | `/api/player_stats?type=` | Get player stats (16 types, see below) |
| GET | `/api/stats/:domain?category=` | Detail stats (domain: battle/craft/item) |
| GET | `/api/stats/:domain/summary?category=&limit=` | Stats summary Top N (default limit=10) |
| POST | `/api/scan` | `{"folder":"...","date":"..."}` Scan a single folder |
| POST | `/api/batch_scan` | `{"parent_folder":"..."}` Batch scan parent folder |
| POST | `/api/export` | Export data to JSON |
| DELETE | `/api/delete_date` | `{"date":"..."}` Delete data for a date |
| DELETE | `/api/batch_delete` | `{"dates":["...","..."]}` Batch delete dates |

> Backward compatible: `/api/battle_stats`, `/api/craft_stats`, `/api/item_stats`, `/api/battle_summary` are still available, all mapped to the unified `/api/stats/:domain` interface.

**player_stats supported type values:** `play_time`, `deaths`, `mob_kills`, `player_kills`, `jumps`, `damage_dealt`, `distance_walked`, `sprint_one_cm`, `walk_one_cm`, `fly_one_cm`, `climb_one_cm`, `swim_one_cm`, `horse_one_cm`, `boat_one_cm`, `aviate_one_cm`, `fall_one_cm`

## Data Export

```bash
uv run python scripts/export_data.py
```

Reads from `mc_stats.db` and exports to `data.json`.

## Data Migration (Upgrade from Legacy)

If upgrading from the legacy monolithic architecture (`mc_stats_server.py`):

```bash
uv run python scripts/migrate_db.py
```

This script merges the old `battle_stats` / `craft_stats` / `item_stats` tables into the unified `detail_stats` table.

## Tech Stack

| Component | Technology |
|:----------|:----------:|
| Frontend Framework | Vue 3 + TypeScript (Composition API) |
| Build Tool | Vite 5 |
| Chart Library | Chart.js 4 + vue-chartjs |
| Internationalization | vue-i18n |
| State Management | Pinia |
| UI Style | Material You Design |
| Backend | Python Flask 3 (Layered Architecture) |
| Database | SQLite (WAL Mode) |
| Package Manager | uv (Python) + npm (Node.js) |
| Deployment | Flask local server / GitHub Pages |

## Project Structure

```
stat/
├── frontend/                          # Vue 3 + Vite Frontend
│   ├── src/
│   │   ├── main.ts                    # Vue entry point
│   │   ├── App.vue                    # Root component
│   │   ├── router/index.ts            # Vue Router configuration
│   │   ├── stores/
│   │   │   ├── app.ts                 # Global state (mode/loading)
│   │   │   └── data.ts                # Statistics data state management
│   │   ├── services/
│   │   │   ├── api.ts                 # API call layer
│   │   │   └── usePlayerFilter.ts     # Player filter composable
│   │   ├── i18n/
│   │   │   ├── index.ts               # vue-i18n configuration
│   │   │   ├── zh-CN.json             # Chinese translations
│   │   │   └── en-US.json             # English translations
│   │   ├── components/
│   │   │   ├── AppLayout.vue          # Layout container
│   │   │   ├── Sidebar.vue            # Sidebar navigation
│   │   │   ├── TopBar.vue             # Top navigation bar
│   │   │   └── PlayerFilter.vue       # Player filter component
│   │   └── pages/
│   │       ├── DashboardPage.vue      # Dashboard overview
│   │       ├── MapStatsPage.vue       # Map statistics
│   │       ├── PlayerStatsPage.vue    # Player statistics
│   │       ├── BattleStatsPage.vue    # Battle statistics
│   │       ├── CraftStatsPage.vue     # Crafting statistics
│   │       ├── ItemStatsPage.vue      # Item statistics
│   │       └── ActivityPage.vue       # Activity statistics
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
│   │   └── exporter.py               # Data export service
│   └── routes/
│       └── api.py                     # All API Blueprint routes
│
├── locales/                           # Standalone translation files (static mode)
│   ├── zh-CN.json
│   └── en-US.json
├── scripts/
│   ├── export_data.py                 # Data export script
│   └── migrate_db.py                 # Data migration script
├── assets/
│   └── icon.png
├── mc_stats.db                        # SQLite database
├── data.json                          # Exported static data
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
services/         ← Business logic (parsing / scanning / exporting)
    ↓
database/         ← Repository pattern data access layer
    ↓
mc_stats.db       ← SQLite database (WAL mode)
```

### Frontend State Management

```
pages/            ← Vue page components (lazy-loaded by route)
    ↓
components/       ← Reusable UI components
    ↓
stores/           ← Pinia Stores (app + data)
    ↓
services/api.ts   ← Unified API calls (auto-switch local/static mode)
```

## Frontend Routes

| Path | Page Component | Description |
|:-----|:---------------|:------------|
| `#/` | DashboardPage | Dashboard overview |
| `#/map` | MapStatsPage | Map size trends |
| `#/players` | PlayerStatsPage | 16 player data categories |
| `#/battle` | BattleStatsPage | Battle kill statistics |
| `#/craft` | CraftStatsPage | Item crafting statistics |
| `#/items` | ItemStatsPage | Pickup/drop/use statistics |
| `#/activity` | ActivityPage | 9 activity distance statistics |

> Uses Hash router (`createWebHashHistory`) for GitHub Pages static deployment compatibility.

## Development Notes

- The frontend proxies `/api/*` requests to the Flask backend at `localhost:5000` via Vite proxy
- In static mode, the frontend reads `data.json` from root; place it in `frontend/public/` during build
- The database uses SQLite WAL mode for improved concurrent read/write performance
- The `detail_stats` table unifies battle/craft/item statistics via the `stat_domain` field; adding a new stat type only requires writing data with a new domain
- The backend `services/parser.py` provides a generic `parse_detail_stats_by_domain()` function that accepts a domain and categories dict to parse any stat type
- `services/scanner.py` batch scanning auto-detects dates from folder names (supports `YYYY-MM-DD`, `YYYY.MM.DD`, `MM.DD` formats)
- `scripts/migrate_db.py` merges legacy tables (battle_stats / craft_stats / item_stats) into detail_stats, then drops old tables

## Acknowledgments

- [Chart.js](https://www.chartjs.org/) - Powerful open-source chart library
- [Vue.js](https://vuejs.org/) - The Progressive JavaScript Framework
- [Flask](https://flask.palletsprojects.com/) - Python micro framework

## License

This project is licensed under the [MIT](https://opensource.org/licenses/MIT) license.