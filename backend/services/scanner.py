import os
import re
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
    parse_detail_stats,
    parse_battle_stats,
    parse_craft_stats,
    parse_item_stats,
    parse_block_stats,
    DOMAIN_CATEGORIES,
)
from backend.services.archiver import (
    is_archive_file,
    ArchiveTempExtractor,
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


def parse_date_from_server_properties(server_folder: str) -> str:
    props_path = os.path.join(server_folder, 'server.properties')
    if not os.path.exists(props_path):
        raise ValueError('server.properties 文件不存在')

    with open(props_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    patterns = [
        r'#\w{3}\s+(\w{3})\s+(\d{1,2})\s+\d{2}:\d{2}:\d{2}\s+\w{3,4}\s+(\d{4})',
        r'#(\d{4})-(\d{1,2})-(\d{1,2})',
        r'#(\d{1,2})/(\d{1,2})/(\d{4})',
    ]

    month_map = {
        'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04',
        'May': '05', 'Jun': '06', 'Jul': '07', 'Aug': '08',
        'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12',
    }

    for line in content.splitlines():
        if not line.startswith('#'):
            continue

        match = re.search(patterns[0], line)
        if match:
            month_str, day, year = match.group(1), match.group(2), match.group(3)
            month = month_map.get(month_str)
            if month:
                return f"{year}-{month}-{day.zfill(2)}"

        match = re.search(patterns[1], line)
        if match:
            year, month, day = match.group(1), match.group(2), match.group(3)
            return f"{year}-{month.zfill(2)}-{day.zfill(2)}"

        match = re.search(patterns[2], line)
        if match:
            month, day, year = match.group(1), match.group(2), match.group(3)
            return f"{year}-{month.zfill(2)}-{day.zfill(2)}"

    raise ValueError('无法从 server.properties 解析日期')


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


def should_include_player(player_name: str, play_time_seconds: int,
                          filter_config: dict) -> bool:
    if not filter_config.get('filter_enabled', False):
        return True

    whitelist = set(filter_config.get('whitelist', []))
    blacklist = set(filter_config.get('blacklist', []))
    min_hours = filter_config.get('min_playtime_hours', 1)

    if whitelist:
        return player_name in whitelist
    if player_name in blacklist:
        return False
    if play_time_seconds >= min_hours * 3600:
        return True
    return False


def parse_all_stats(stats_folder: str):
    import json as _json
    from pathlib import Path

    player_stats = {}
    all_details = {'battle': {}, 'craft': {}, 'item': {}, 'block': {}}
    stats_path = Path(stats_folder)

    if not stats_path.exists():
        return player_stats, all_details

    for stat_file in stats_path.glob('*.json'):
        player_uuid = stat_file.stem
        try:
            with open(stat_file, 'r', encoding='utf-8') as f:
                data = _json.load(f)

            stats = data.get('stats', {})
            custom = stats.get('minecraft:custom', {})
            player_data = {
                'play_time': custom.get('minecraft:play_time', 0) // 20,
                'deaths': custom.get('minecraft:deaths', 0),
                'mob_kills': custom.get('minecraft:mob_kills', 0),
                'player_kills': custom.get('minecraft:player_kills', 0),
                'damage_dealt': custom.get('minecraft:damage_dealt', 0),
                'damage_taken': custom.get('minecraft:damage_taken', 0),
                'distance_walked': custom.get('minecraft:walk_one_cm', 0) // 100,
                'jumps': custom.get('minecraft:jump', 0),
                'sprint_one_cm': custom.get('minecraft:sprint_one_cm', 0),
                'walk_one_cm': custom.get('minecraft:walk_one_cm', 0),
                'fly_one_cm': custom.get('minecraft:fly_one_cm', 0),
                'climb_one_cm': custom.get('minecraft:climb_one_cm', 0),
                'swim_one_cm': custom.get('minecraft:swim_one_cm', 0),
                'horse_one_cm': custom.get('minecraft:horse_one_cm', 0),
                'boat_one_cm': custom.get('minecraft:boat_one_cm', 0),
                'aviate_one_cm': custom.get('minecraft:aviate_one_cm', 0),
                'fall_one_cm': custom.get('minecraft:fall_one_cm', 0),
                'sleep_in_bed': custom.get('minecraft:sleep_in_bed', 0),
                'fish_caught': custom.get('minecraft:fish_caught', 0),
                'animals_bred': custom.get('minecraft:animals_bred', 0),
                'traded_with_villager': custom.get('minecraft:traded_with_villager', 0),
                'talked_to_villager': custom.get('minecraft:talked_to_villager', 0),
                'enchant_item': custom.get('minecraft:enchant_item', 0),
                'interact_with_crafting_table': custom.get('minecraft:interact_with_crafting_table', 0),
                'interact_with_furnace': custom.get('minecraft:interact_with_furnace', 0),
                'interact_with_anvil': custom.get('minecraft:interact_with_anvil', 0),
                'open_chest': custom.get('minecraft:open_chest', 0),
                'bell_ring': custom.get('minecraft:bell_ring', 0),
                'drop_count': custom.get('minecraft:drop', 0),
                'eat_cake_slice': custom.get('minecraft:eat_cake_slice', 0),
                'sneak_time': custom.get('minecraft:sneak_time', 0) // 20,
                'leave_game': custom.get('minecraft:leave_game', 0),
            }
            player_stats[player_uuid] = player_data

            for domain, categories in DOMAIN_CATEGORIES.items():
                player_detail = {}
                for category_key, category_name in categories.items():
                    category_data = stats.get(category_name, {})
                    for item_key, count in category_data.items():
                        simplified_key = item_key.replace('minecraft:', '')
                        player_detail[f"{category_key}:{simplified_key}"] = count
                if player_detail:
                    all_details[domain][player_uuid] = player_detail

        except Exception as e:
            print(f"Error parsing {stat_file}: {e}")

    return player_stats, all_details


def scan_server_folder(server_folder: str, date: str = None,
                       filter_config: dict = None,
                       conn: Optional[sqlite3.Connection] = None) -> dict:
    if filter_config is None:
        filter_config = {}

    if date is None:
        date = parse_date_from_server_properties(server_folder)

    own_conn = conn is None
    if own_conn:
        conn = get_connection()

    uuid_to_name = load_usercache(server_folder)

    map_data = scan_map_sizes(server_folder, date, conn)

    stats_folder = os.path.join(server_folder, 'world', 'players', 'stats')
    player_stats, all_details = parse_all_stats(stats_folder)
    total_players = len(player_stats)
    filtered_count = 0

    player_rows = []
    for player_uuid, stats in player_stats.items():
        player_name = uuid_to_name.get(player_uuid, player_uuid)
        play_time_seconds = stats.get('play_time', 0)
        if not should_include_player(player_name, play_time_seconds, filter_config):
            filtered_count += 1
            continue
        for stat_type, stat_value in stats.items():
            player_rows.append((date, player_name, stat_type, stat_value))

    if player_rows:
        PlayerStatsRepository.insert_many(player_rows, conn)

    detail_rows = []
    detail_counts = {'battle': 0, 'craft': 0, 'item': 0, 'block': 0}

    for domain in ('battle', 'craft', 'item', 'block'):
        for player_uuid, stats in all_details[domain].items():
            player_name = uuid_to_name.get(player_uuid, player_uuid)
            play_time_seconds = player_stats.get(player_uuid, {}).get('play_time', 0)
            if not should_include_player(player_name, play_time_seconds, filter_config):
                continue
            for stat_key, stat_value in stats.items():
                parts = stat_key.split(':', 1)
                if len(parts) == 2:
                    stat_category, item_name = parts
                    detail_rows.append((date, player_name, domain, stat_category, item_name, stat_value))
                    detail_counts[domain] += 1

    if detail_rows:
        DetailStatsRepository.insert_many(detail_rows, conn)

    if own_conn:
        conn.commit()
        conn.close()

    result = {
        'date': date,
        'maps': map_data,
        'player_count': total_players - filtered_count,
        'battle_stats_count': detail_counts['battle'],
        'craft_stats_count': detail_counts['craft'],
        'item_stats_count': detail_counts['item'],
        'block_stats_count': detail_counts['block'],
    }

    if filtered_count > 0:
        result['filtered_count'] = filtered_count
        result['total_players'] = total_players

    return result


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


def batch_scan_parent_folder(parent_folder: str,
                             filter_config: dict = None) -> dict:
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
                date = parse_date_from_server_properties(item_path)
            except ValueError:
                try:
                    date = parse_date_from_folder_name(folder_name)
                except ValueError:
                    mtime = os.path.getmtime(item_path)
                    date = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d')

            try:
                scan_result = scan_server_folder(item_path, date, filter_config=filter_config)
                result_entry = {
                    'folder': folder_name,
                    'date': date,
                    'success': True,
                    'maps': scan_result['maps'],
                    'player_count': scan_result['player_count'],
                }
                if scan_result.get('filtered_count', 0) > 0:
                    result_entry['filtered_count'] = scan_result['filtered_count']
                    result_entry['total_players'] = scan_result['total_players']
                results.append(result_entry)
            except Exception as e:
                errors.append({'folder': folder_name, 'error': str(e)})

        total_filtered = sum(r.get('filtered_count', 0) for r in results)
        total_players_all = sum(r.get('total_players', r.get('player_count', 0)) for r in results)

        response = {
            'success': True,
            'total': len(results) + len(errors),
            'imported': len(results),
            'failed': len(errors),
            'results': results,
            'errors': errors,
        }

        if total_filtered > 0:
            response['filtered_count'] = total_filtered
            response['total_players'] = total_players_all

        return response

    except Exception as e:
        return {'error': str(e)}


def scan_archive(archive_path: str, date: str = None,
                 filter_config: dict = None,
                 conn: Optional[sqlite3.Connection] = None) -> dict:
    extractor = ArchiveTempExtractor()
    try:
        server_folder = extractor.extract(archive_path)
        if not os.path.exists(os.path.join(server_folder, 'world')):
            raise ValueError('压缩包内未找到 world 目录，无法识别为有效的服务器备份')
        result = scan_server_folder(server_folder, date=date,
                                    filter_config=filter_config, conn=conn)
        return result
    finally:
        extractor.cleanup()


def _collect_scannable_items(parent_folder: str):
    from backend.services.archiver import get_archive_extension

    items = []
    for item_name in sorted(os.listdir(parent_folder)):
        item_path = os.path.join(parent_folder, item_name)

        if os.path.isdir(item_path):
            world_path = os.path.join(item_path, 'world')
            if os.path.exists(world_path):
                items.append({
                    'type': 'folder',
                    'name': item_name,
                    'path': item_path,
                })
        elif os.path.isfile(item_path) and is_archive_file(item_path):
            items.append({
                'type': 'archive',
                'name': item_name,
                'path': item_path,
            })

    return items


def _resolve_item_date(item: dict):
    from backend.services.archiver import ArchiveTempExtractor

    if item['type'] == 'folder':
        try:
            date = parse_date_from_server_properties(item['path'])
        except ValueError:
            try:
                date = parse_date_from_folder_name(item['name'])
            except ValueError:
                mtime = os.path.getmtime(item['path'])
                date = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d')
        return date
    else:
        extractor = ArchiveTempExtractor()
        try:
            server_folder = extractor.extract(item['path'])
            try:
                date = parse_date_from_server_properties(server_folder)
            except ValueError:
                try:
                    date = parse_date_from_folder_name(item['name'])
                except ValueError:
                    mtime = os.path.getmtime(item['path'])
                    date = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d')
            return date
        finally:
            extractor.cleanup()


def batch_scan_parent_folder_v2(parent_folder: str,
                                 filter_config: dict = None) -> dict:
    results = []
    errors = []

    try:
        items = _collect_scannable_items(parent_folder)

        for item in items:
            extractor = None
            try:
                if item['type'] == 'archive':
                    extractor = ArchiveTempExtractor()
                    server_folder = extractor.extract(item['path'])
                else:
                    server_folder = item['path']

                date = _resolve_item_date(item) if item['type'] == 'folder' else None
                if date is None:
                    try:
                        date = parse_date_from_server_properties(server_folder)
                    except ValueError:
                        try:
                            date = parse_date_from_folder_name(item['name'])
                        except ValueError:
                            mtime = os.path.getmtime(item['path'])
                            date = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d')

                scan_result = scan_server_folder(server_folder, date,
                                                 filter_config=filter_config)
                result_entry = {
                    'folder': item['name'],
                    'date': date,
                    'success': True,
                    'type': item['type'],
                    'maps': scan_result['maps'],
                    'player_count': scan_result['player_count'],
                }
                if scan_result.get('filtered_count', 0) > 0:
                    result_entry['filtered_count'] = scan_result['filtered_count']
                    result_entry['total_players'] = scan_result['total_players']
                results.append(result_entry)
            except Exception as e:
                errors.append({'folder': item['name'], 'error': str(e)})
            finally:
                if extractor:
                    extractor.cleanup()

        total_filtered = sum(r.get('filtered_count', 0) for r in results)
        total_players_all = sum(r.get('total_players', r.get('player_count', 0)) for r in results)

        response = {
            'success': True,
            'total': len(results) + len(errors),
            'imported': len(results),
            'failed': len(errors),
            'results': results,
            'errors': errors,
        }

        if total_filtered > 0:
            response['filtered_count'] = total_filtered
            response['total_players'] = total_players_all

        return response

    except Exception as e:
        return {'error': str(e)}
