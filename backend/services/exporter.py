import json
import os
from datetime import datetime
from pathlib import Path

from backend.config import DB_FILE, DATA_JSON
from backend.database.repositories import (
    ServerRepository,
    MapSizeRepository,
    PlayerStatsRepository,
    DetailStatsRepository,
)

SERVERS_JSON = str(Path(DATA_JSON).parent / 'servers.json')


def export_all() -> dict:
    return {
        'exported_at': datetime.now().isoformat(),
        'map_sizes': MapSizeRepository.get_all(),
        'player_stats': PlayerStatsRepository.get_all(),
        'detail_stats': DetailStatsRepository.get_all(),
    }


def export_by_server() -> dict:
    """Export data grouped by server name."""
    servers = ServerRepository.get_all()
    result: dict = {'exported_at': datetime.now().isoformat(), 'servers': {}}

    for server_name in servers:
        result['servers'][server_name] = {
            'map_sizes': MapSizeRepository.get_all(server_name),
            'player_stats': PlayerStatsRepository.get_all(server_name),
            'detail_stats': DetailStatsRepository.get_all(server_name),
        }

    # Also include data without a server (legacy / default)
    default_data = {
        'map_sizes': MapSizeRepository.get_all(None),
        'player_stats': PlayerStatsRepository.get_all(None),
        'detail_stats': DetailStatsRepository.get_all(None),
    }
    # If there are no servers at all, put everything under 'default'
    if not servers:
        result['servers']['default'] = default_data
    else:
        # Check if there's data not belonging to any named server
        has_default_data = (
            default_data['map_sizes'] or
            default_data['player_stats'] or
            default_data['detail_stats']
        )
        if has_default_data:
            result['servers']['default'] = default_data

    return result


def export_to_json():
    data = export_by_server()
    with open(DATA_JSON, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    # Write servers list
    servers = ServerRepository.get_all()
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
