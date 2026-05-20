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


def load_usercache_from_content(content: str) -> Dict[str, str]:
    uuid_to_name = {}
    try:
        usercache = json.loads(content)
        for entry in usercache:
            uuid = entry.get('uuid', '')
            name = entry.get('name', '')
            if uuid and name:
                uuid_to_name[uuid] = name
    except Exception as e:
        print(f"Error parsing usercache content: {e}")
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
        except Exception as e:
            print(f"Error parsing {stat_file}: {e}")

    return player_stats


def _extract_player_data(data: dict) -> dict:
    stats = data.get('stats', {})
    custom = stats.get('minecraft:custom', {})
    return {
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


def parse_all_stats(stats_folder: str):
    player_stats = {}
    all_details = {'battle': {}, 'craft': {}, 'item': {}, 'block': {}}
    stats_path = Path(stats_folder)

    if not stats_path.exists():
        return player_stats, all_details

    for stat_file in stats_path.glob('*.json'):
        player_uuid = stat_file.stem
        try:
            with open(stat_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            player_stats[player_uuid] = _extract_player_data(data)

            for domain, categories in DOMAIN_CATEGORIES.items():
                player_detail = {}
                for category_key, category_name in categories.items():
                    category_data = data.get('stats', {}).get(category_name, {})
                    for item_key, count in category_data.items():
                        simplified_key = item_key.replace('minecraft:', '')
                        player_detail[f"{category_key}:{simplified_key}"] = count
                if player_detail:
                    all_details[domain][player_uuid] = player_detail

        except Exception as e:
            print(f"Error parsing {stat_file}: {e}")

    return player_stats, all_details


def parse_all_stats_from_contents(stats_contents: dict):
    player_stats = {}
    all_details = {'battle': {}, 'craft': {}, 'item': {}, 'block': {}}

    for player_uuid, content in stats_contents.items():
        try:
            data = json.loads(content)

            player_stats[player_uuid] = _extract_player_data(data)

            for domain, categories in DOMAIN_CATEGORIES.items():
                player_detail = {}
                for category_key, category_name in categories.items():
                    category_data = data.get('stats', {}).get(category_name, {})
                    for item_key, count in category_data.items():
                        simplified_key = item_key.replace('minecraft:', '')
                        player_detail[f"{category_key}:{simplified_key}"] = count
                if player_detail:
                    all_details[domain][player_uuid] = player_detail

        except Exception as e:
            print(f"Error parsing stats for {player_uuid}: {e}")

    return player_stats, all_details


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

BLOCK_CATEGORIES = {
    'mined': 'minecraft:mined',
    'broken': 'minecraft:broken',
}


def parse_battle_stats(stats_folder: str) -> dict:
    return parse_detail_stats(stats_folder, 'battle', BATTLE_CATEGORIES)


def parse_craft_stats(stats_folder: str) -> dict:
    return parse_detail_stats(stats_folder, 'craft', CRAFT_CATEGORIES)


def parse_item_stats(stats_folder: str) -> dict:
    return parse_detail_stats(stats_folder, 'item', ITEM_CATEGORIES)


def parse_block_stats(stats_folder: str) -> dict:
    return parse_detail_stats(stats_folder, 'block', BLOCK_CATEGORIES)


DOMAIN_CATEGORIES = {
    'battle': BATTLE_CATEGORIES,
    'craft': CRAFT_CATEGORIES,
    'item': ITEM_CATEGORIES,
    'block': BLOCK_CATEGORIES,
}


def parse_detail_stats_by_domain(stats_folder: str, stat_domain: str) -> dict:
    categories = DOMAIN_CATEGORIES.get(stat_domain, {})
    return parse_detail_stats(stats_folder, stat_domain, categories)
