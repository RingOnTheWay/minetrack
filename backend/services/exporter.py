import json
import sqlite3
from datetime import datetime
from pathlib import Path

from backend.config import DB_FILE, DATA_JSON
from backend.database.repositories import (
    MapSizeRepository,
    PlayerStatsRepository,
    DetailStatsRepository,
)

SERVERS_JSON = str(Path(DATA_JSON).parent / 'servers.json')


def get_distinct_server_names() -> list[str]:
    """Get all distinct server_name values from data tables."""
    conn = sqlite3.connect(DB_FILE)
    rows = conn.execute(
        'SELECT DISTINCT server_name FROM ('
        '  SELECT server_name FROM map_sizes UNION'
        '  SELECT server_name FROM player_stats UNION'
        '  SELECT server_name FROM detail_stats'
        ') ORDER BY server_name'
    ).fetchall()
    conn.close()
    return [row[0] for row in rows]


def export_by_server() -> dict:
    """Export data grouped by server name."""
    server_names = get_distinct_server_names()
    result: dict = {'exported_at': datetime.now().isoformat(), 'servers': {}}

    for name in server_names:
        result['servers'][name] = {
            'map_sizes': MapSizeRepository.get_all(name),
            'player_stats': PlayerStatsRepository.get_all(name),
            'detail_stats': DetailStatsRepository.get_all(name),
        }

    # Fallback: if no data at all, create empty default
    if not result['servers']:
        result['servers']['default'] = {
            'map_sizes': {},
            'player_stats': {},
            'detail_stats': {},
        }

    return result


def export_to_json():
    data = export_by_server()
    with open(DATA_JSON, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    server_names = list(data['servers'].keys())
    with open(SERVERS_JSON, 'w', encoding='utf-8') as f:
        json.dump(server_names, f, ensure_ascii=False, indent=2)

    print(f"数据已导出到 {DATA_JSON}")
    print(f"服务器列表已导出到 {SERVERS_JSON}")
    for sn in server_names:
        sd = data['servers'][sn]
        stat_count = len(sd.get('player_stats', {}))
        map_count = len(sd.get('map_sizes', {}))
        print(f"  [{sn}] 地图尺寸: {map_count} 天, 统计类型: {stat_count} 种")

    return data
