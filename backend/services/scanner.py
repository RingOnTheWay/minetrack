import os
import re
import sqlite3
import tempfile
import shutil
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
    load_usercache_from_content,
    parse_player_stats,
    parse_all_stats,
    parse_all_stats_from_contents,
    parse_detail_stats,
    parse_battle_stats,
    parse_craft_stats,
    parse_item_stats,
    parse_block_stats,
    DOMAIN_CATEGORIES,
)
from backend.services.archiver import (
    is_archive_file,
    ArchiveReader,
    _find_server_folder,
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


def _parse_date_from_content(content: str) -> str:
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


def parse_date_from_server_properties(server_folder: str) -> str:
    props_path = os.path.join(server_folder, 'server.properties')
    if not os.path.exists(props_path):
        raise ValueError('server.properties 文件不存在')
    with open(props_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    return _parse_date_from_content(content)


def scan_map_sizes(server_folder: str, date: str, server_name: str = 'default',
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
                MapSizeRepository.insert_or_replace(server_name, date, map_name, size_mb, conn)
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


def scan_server_folder(server_folder: str, date: str = None,
                       server_name: str = 'default',
                       filter_config: dict = None,
                       conn: Optional[sqlite3.Connection] = None,
                       map_sizes_override: list = None,
                       usercache_override: dict = None,
                       stats_contents_override: dict = None) -> dict:
    if filter_config is None:
        filter_config = {}

    if date is None:
        date = parse_date_from_server_properties(server_folder)

    own_conn = conn is None
    if own_conn:
        conn = get_connection()

    if usercache_override is not None:
        uuid_to_name = usercache_override
    else:
        uuid_to_name = load_usercache(server_folder)

    if map_sizes_override is not None:
        map_data = map_sizes_override
        for ms in map_data:
            MapSizeRepository.insert_or_replace(server_name, date, ms['name'], ms['size'], conn)
    else:
        map_data = scan_map_sizes(server_folder, date, server_name, conn)

    if stats_contents_override is not None:
        player_stats, all_details = parse_all_stats_from_contents(stats_contents_override)
    else:
        stats_folder = os.path.join(server_folder, 'world', 'players', 'stats')
        if not os.path.exists(stats_folder):
            stats_folder = os.path.join(server_folder, 'world', 'stats')
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
            player_rows.append((server_name, date, player_name, stat_type, stat_value))

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
                    detail_rows.append((server_name, date, player_name, domain, stat_category, item_name, stat_value))
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
                             server_name: str = 'default',
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
                scan_result = scan_server_folder(item_path, date, server_name=server_name,
                                                 filter_config=filter_config)
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
                 server_name: str = 'default',
                 filter_config: dict = None,
                 conn: Optional[sqlite3.Connection] = None) -> dict:
    reader = ArchiveReader(archive_path)
    for _ in reader.read_needed_gen():
        pass

    data = reader.needed_data
    if not data or not data.get('server_properties'):
        raise ValueError('压缩包内未找到 server.properties')

    if date is None:
        try:
            date = _parse_date_from_content(data['server_properties'])
        except ValueError:
            try:
                date = parse_date_from_folder_name(os.path.basename(archive_path))
            except ValueError:
                mtime = os.path.getmtime(archive_path)
                date = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d')

    uuid_to_name = {}
    if data.get('usercache'):
        uuid_to_name = load_usercache_from_content(data['usercache'])

    map_sizes = reader.compute_map_sizes()

    stats_contents = data.get('stats', {})

    result = scan_server_folder(
        '', date=date, server_name=server_name, filter_config=filter_config, conn=conn,
        map_sizes_override=map_sizes,
        usercache_override=uuid_to_name,
        stats_contents_override=stats_contents,
    )

    return result


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
        reader = ArchiveReader(item['path'])
        try:
            props_content = reader.read_file_text('server.properties')
            if props_content:
                try:
                    return _parse_date_from_content(props_content)
                except ValueError:
                    pass
            try:
                return parse_date_from_folder_name(item['name'])
            except ValueError:
                mtime = os.path.getmtime(item['path'])
                return datetime.fromtimestamp(mtime).strftime('%Y-%m-%d')
        finally:
            pass


def batch_scan_parent_folder_v2(parent_folder: str,
                                 server_name: str = 'default',
                                 filter_config: dict = None) -> dict:
    results = []
    errors = []

    try:
        items = _collect_scannable_items(parent_folder)

        for item in items:
            try:
                if item['type'] == 'archive':
                    scan_result = scan_archive(item['path'], server_name=server_name,
                                               filter_config=filter_config)
                else:
                    date = _resolve_item_date(item)
                    scan_result = scan_server_folder(item['path'], date,
                                                     server_name=server_name,
                                                     filter_config=filter_config)

                date = scan_result['date']
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
