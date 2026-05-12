import json
import os
from pathlib import Path
from typing import Dict


def load_usercache(server_folder: str) -> Dict[str, str]:
    usercache_path = os.path.join(server_folder, 'usercache.json')
    uuid_to_name = {}

    try:
        if os.path.exists(usercache_path):
            with open(usercache_path, 'r', encoding='utf-8') as f:
                usercache = json.load(f)
                for entry in usercache:
                    uuid = entry.get('uuid', '')
                    name = entry.get('name', '')
                    if uuid and name:
                        uuid_to_name[uuid] = name
    except Exception as e:
        print(f"Error loading usercache.json: {e}")

    return uuid_to_name


def parse_player_stats(stats_folder: str) -> dict:
    player_stats = {}
    stats_path = Path(stats_folder)

    if not stats_path.exists():
        return player_stats

    for stat_file in stats_path.glob('*.json'):
        player_uuid = stat_file.stem
        try:
            with open(stat_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            stats = data.get('stats', {})
            custom = stats.get('minecraft:custom', {})
            player_data = {
                'play_time': custom.get('minecraft:play_time', 0) // 20,
                'deaths': custom.get('minecraft:deaths', 0),
                'mob_kills': custom.get('minecraft:mob_kills', 0),
                'player_kills': custom.get('minecraft:player_kills', 0),
                'damage_dealt': custom.get('minecraft:damage_dealt', 0),
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
            }
            player_stats[player_uuid] = player_data
        except Exception as e:
            print(f"Error parsing {stat_file}: {e}")

    return player_stats


def parse_detail_stats(stats_folder: str, stat_domain: str,
                       categories: Dict[str, str]) -> dict:
    detail_stats = {}
    stats_path = Path(stats_folder)

    if not stats_path.exists():
        return detail_stats

    for stat_file in stats_path.glob('*.json'):
        player_uuid = stat_file.stem
        try:
            with open(stat_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            stats = data.get('stats', {})

            player_data = {}
            for category_key, category_name in categories.items():
                category_data = stats.get(category_name, {})
                for item_key, count in category_data.items():
                    simplified_key = item_key.replace('minecraft:', '')
                    player_data[f"{category_key}:{simplified_key}"] = count

            if player_data:
                detail_stats[player_uuid] = player_data

        except Exception as e:
            print(f"Error parsing detail stats {stat_file}: {e}")

    return detail_stats


BATTLE_CATEGORIES = {
    'killed': 'minecraft:killed',
    'killed_by': 'minecraft:killed_by',
}

CRAFT_CATEGORIES = {
    'crafted': 'minecraft:crafted',
    'used': 'minecraft:used',
}

ITEM_CATEGORIES = {
    'picked_up': 'minecraft:picked_up',
    'dropped': 'minecraft:dropped',
    'used': 'minecraft:used',
}


def parse_battle_stats(stats_folder: str) -> dict:
    return parse_detail_stats(stats_folder, 'battle', BATTLE_CATEGORIES)


def parse_craft_stats(stats_folder: str) -> dict:
    return parse_detail_stats(stats_folder, 'craft', CRAFT_CATEGORIES)


def parse_item_stats(stats_folder: str) -> dict:
    return parse_detail_stats(stats_folder, 'item', ITEM_CATEGORIES)


DOMAIN_CATEGORIES = {
    'battle': BATTLE_CATEGORIES,
    'craft': CRAFT_CATEGORIES,
    'item': ITEM_CATEGORIES,
}


def parse_detail_stats_by_domain(stats_folder: str, stat_domain: str) -> dict:
    categories = DOMAIN_CATEGORIES.get(stat_domain, {})
    return parse_detail_stats(stats_folder, stat_domain, categories)