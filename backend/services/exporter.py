import json
import os
from datetime import datetime
from pathlib import Path

from backend.config import DB_FILE, DATA_JSON
from backend.database.repositories import (
    MapSizeRepository,
    PlayerStatsRepository,
    DetailStatsRepository,
)


def export_all() -> dict:
    return {
        'exported_at': datetime.now().isoformat(),
        'map_sizes': MapSizeRepository.get_all(),
        'player_stats': PlayerStatsRepository.get_all(),
        'detail_stats': DetailStatsRepository.get_all(),
    }


def export_to_json():
    data = export_all()
    with open(DATA_JSON, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    stats = data['player_stats']
    print(f"数据已导出到 {DATA_JSON}")
    print(f"- 地图尺寸记录：{len(data['map_sizes'])} 天")
    print(f"- 玩家统计类型：{len(stats)} 种")
    print(f"- 详细统计 domain 数：{len(data['detail_stats'])} 种")

    dates = sorted(data['map_sizes'].keys())
    if dates:
        print(f"- 日期范围：{dates[0]} 至 {dates[-1]}")

    return data