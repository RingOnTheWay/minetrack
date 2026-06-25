import json
from datetime import datetime
from pathlib import Path

from backend.config import DATA_JSON
from backend.database.repositories import (
    ServerRepository,
    MapSizeRepository,
    PlayerStatsRepository,
    DetailStatsRepository,
)

SERVERS_JSON = str(Path(DATA_JSON).parent / 'servers.json')


def export_by_server() -> dict:
    """Export data grouped by server name from servers table."""
    server_names = ServerRepository.get_all()

    result: dict = {'exported_at': datetime.now().isoformat(), 'servers': {}}

    for name in server_names:
        result['servers'][name] = {
            'map_sizes': MapSizeRepository.get_all(name),
            'player_stats': PlayerStatsRepository.get_all(name),
            'detail_stats': DetailStatsRepository.get_all(name),
        }

    # Fallback: if no servers at all, create empty default
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
