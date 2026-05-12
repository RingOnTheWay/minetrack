import os
import sqlite3
from datetime import datetime
from typing import Optional

from backend.config import DB_FILE
from backend.database.repositories import (
    get_connection,
    MapSizeRepository,
    PlayerStatsRepository,
    DetailStatsRepository,
)
from backend.services.parser import (
    load_usercache,
    parse_player_stats,
    parse_detail_stats_by_domain,
    parse_battle_stats,
    parse_craft_stats,
    parse_item_stats,
)


def get_folder_size(folder_path: str) -> float:
    total_size = 0
    try:
        for dirpath, _, filenames in os.walk(folder_path):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                if os.path.exists(filepath):
                    total_size += os.path.getsize(filepath)
    except Exception as e:
        print(f"Error calculating size for {folder_path}: {e}")
    return total_size / (1024 * 1024)


MAP_FOLDERS = [
    ('world', ['world', 'world/dimensions/minecraft/overworld']),
    ('world_nether', ['world_nether', 'world/dimensions/minecraft/the_nether']),
    ('world_the_end', ['world_the_end', 'world/dimensions/minecraft/the_end']),
]


def scan_map_sizes(server_folder: str, date: str,
                   conn: Optional[sqlite3.Connection] = None) -> list:
    close_conn = conn is None
    if close_conn:
        conn = get_connection()

    map_data = []
    for map_name, possible_paths in MAP_FOLDERS:
        for path in possible_paths:
            map_path = os.path.join(server_folder, path)
            if os.path.exists(map_path):
                size_mb = get_folder_size(map_path)
                MapSizeRepository.insert_or_replace(date, map_name, size_mb, conn)
                map_data.append({'name': map_name, 'size': round(size_mb, 2)})
                break

    if close_conn:
        conn.commit()
        conn.close()

    return map_data


def scan_server_folder(server_folder: str, date: str) -> dict:
    conn = get_connection()

    uuid_to_name = load_usercache(server_folder)

    map_data = scan_map_sizes(server_folder, date, conn)

    stats_folder = os.path.join(server_folder, 'world', 'players', 'stats')
    player_stats = parse_player_stats(stats_folder)
    player_count = len(player_stats)

    for player_uuid, stats in player_stats.items():
        player_name = uuid_to_name.get(player_uuid, player_uuid)
        for stat_type, stat_value in stats.items():
            PlayerStatsRepository.insert_or_replace(date, player_name, stat_type, stat_value, conn)

    battle_stats = parse_battle_stats(stats_folder)
    battle_count = 0
    for player_uuid, stats in battle_stats.items():
        player_name = uuid_to_name.get(player_uuid, player_uuid)
        for stat_key, stat_value in stats.items():
            parts = stat_key.split(':', 1)
            if len(parts) == 2:
                stat_category, mob_name = parts
                DetailStatsRepository.insert_or_replace(
                    date, player_name, 'battle', stat_category, mob_name, stat_value, conn
                )
                battle_count += 1

    craft_stats = parse_craft_stats(stats_folder)
    craft_count = 0
    for player_uuid, stats in craft_stats.items():
        player_name = uuid_to_name.get(player_uuid, player_uuid)
        for stat_key, stat_value in stats.items():
            parts = stat_key.split(':', 1)
            if len(parts) == 2:
                stat_category, item_name = parts
                DetailStatsRepository.insert_or_replace(
                    date, player_name, 'craft', stat_category, item_name, stat_value, conn
                )
                craft_count += 1

    item_stats = parse_item_stats(stats_folder)
    item_count = 0
    for player_uuid, stats in item_stats.items():
        player_name = uuid_to_name.get(player_uuid, player_uuid)
        for stat_key, stat_value in stats.items():
            parts = stat_key.split(':', 1)
            if len(parts) == 2:
                stat_category, item_name = parts
                DetailStatsRepository.insert_or_replace(
                    date, player_name, 'item', stat_category, item_name, stat_value, conn
                )
                item_count += 1

    conn.commit()
    conn.close()

    return {
        'maps': map_data,
        'player_count': player_count,
        'battle_stats_count': battle_count,
        'craft_stats_count': craft_count,
        'item_stats_count': item_count,
    }


import re


def parse_date_from_folder_name(folder_name: str) -> str:
    patterns = [
        r'(\d{4})-(\d{1,2})-(\d{1,2})',
        r'(\d{4})\.(\d{1,2})\.(\d{1,2})',
        r'(\d{4})_(\d{1,2})_(\d{1,2})',
        r'(\d{1,2})\.(\d{1,2})',
        r'(\d{1,2})-(\d{1,2})',
    ]

    for pattern in patterns:
        match = re.search(pattern, folder_name)
        if match:
            groups = match.groups()
            if len(groups) == 3:
                year, month, day = groups
                return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
            elif len(groups) == 2:
                month, day = groups
                year = datetime.now().year
                return f"{year}-{month.zfill(2)}-{day.zfill(2)}"

    raise ValueError(f"无法从文件夹名 '{folder_name}' 解析日期")


def batch_scan_parent_folder(parent_folder: str) -> dict:
    results = []
    errors = []

    try:
        for item in os.listdir(parent_folder):
            item_path = os.path.join(parent_folder, item)
            if not os.path.isdir(item_path):
                continue

            world_path = os.path.join(item_path, 'world')
            if not os.path.exists(world_path):
                continue

            folder_name = item
            try:
                date = parse_date_from_folder_name(folder_name)
            except ValueError:
                mtime = os.path.getmtime(item_path)
                date = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d')

            try:
                scan_result = scan_server_folder(item_path, date)
                results.append({
                    'folder': folder_name,
                    'date': date,
                    'success': True,
                    'maps': scan_result['maps'],
                    'player_count': scan_result['player_count'],
                })
            except Exception as e:
                errors.append({'folder': folder_name, 'error': str(e)})

        return {
            'success': True,
            'total': len(results) + len(errors),
            'imported': len(results),
            'failed': len(errors),
            'results': results,
            'errors': errors,
        }

    except Exception as e:
        return {'error': str(e)}