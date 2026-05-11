#!/usr/bin/env python3
"""
导出数据库数据为 JSON 格式，供静态页面使用
使用方法：python scripts/export_data.py
"""
import sqlite3
import json
from datetime import datetime

DB_FILE = 'mc_stats.db'
OUTPUT_FILE = 'data.json'

def export_map_sizes():
    """导出地图大小数据"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT date, map_name, size_mb FROM map_sizes ORDER BY date')
    rows = cursor.fetchall()
    conn.close()

    data = {}
    for date, map_name, size_mb in rows:
        if date not in data:
            data[date] = {}
        data[date][map_name] = round(size_mb, 2)

    return data


def export_player_stats():
    """导出玩家统计数据"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    stats = {}
    cursor.execute('SELECT DISTINCT stat_type FROM player_stats')
    stat_types = [row[0] for row in cursor.fetchall()]

    for stat_type in stat_types:
        cursor.execute('''
            SELECT date, player_name, stat_value
            FROM player_stats
            WHERE stat_type = ?
            ORDER BY date
        ''', (stat_type,))

        rows = cursor.fetchall()
        stat_data = {}

        for date, player_name, stat_value in rows:
            if date not in stat_data:
                stat_data[date] = {}
            stat_data[date][player_name] = stat_value

        stats[stat_type] = stat_data

    conn.close()
    return stats


def export_battle_stats():
    """导出战详细斗统计数据"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    battle_data = {}
    cursor.execute('''
        SELECT date, player_name, stat_category, stat_key, stat_value
        FROM battle_stats
        ORDER BY date, player_name
    ''')

    for date, player_name, stat_category, stat_key, stat_value in cursor.fetchall():
        if stat_category not in battle_data:
            battle_data[stat_category] = {}
        if date not in battle_data[stat_category]:
            battle_data[stat_category][date] = {}
        if player_name not in battle_data[stat_category][date]:
            battle_data[stat_category][date][player_name] = {}
        battle_data[stat_category][date][player_name][stat_key] = stat_value

    conn.close()
    return battle_data


def export_craft_stats():
    """导出物品合成/使用统计数据"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    craft_data = {}
    cursor.execute('''
        SELECT date, player_name, stat_category, stat_key, stat_value
        FROM craft_stats
        ORDER BY date, player_name
    ''')

    for date, player_name, stat_category, stat_key, stat_value in cursor.fetchall():
        if stat_category not in craft_data:
            craft_data[stat_category] = {}
        if date not in craft_data[stat_category]:
            craft_data[stat_category][date] = {}
        if player_name not in craft_data[stat_category][date]:
            craft_data[stat_category][date][player_name] = {}
        craft_data[stat_category][date][player_name][stat_key] = stat_value

    conn.close()
    return craft_data


def export_item_stats():
    """导出物品拾取/丢弃/使用统计数据"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    item_data = {}
    cursor.execute('''
        SELECT date, player_name, stat_category, stat_key, stat_value
        FROM item_stats
        ORDER BY date, player_name
    ''')

    for date, player_name, stat_category, stat_key, stat_value in cursor.fetchall():
        if stat_category not in item_data:
            item_data[stat_category] = {}
        if date not in item_data[stat_category]:
            item_data[stat_category][date] = {}
        if player_name not in item_data[stat_category][date]:
            item_data[stat_category][date][player_name] = {}
        item_data[stat_category][date][player_name][stat_key] = stat_value

    conn.close()
    return item_data


def export_all_data():
    """导出所有数据"""
    return {
        'exported_at': datetime.now().isoformat(),
        'map_sizes': export_map_sizes(),
        'player_stats': export_player_stats(),
        'battle_stats': export_battle_stats(),
        'craft_stats': export_craft_stats(),
        'item_stats': export_item_stats()
    }


def main():
    print("正在导出数据...")

    try:
        data = export_all_data()
    except Exception as e:
        print(f"错误：无法读取数据库 '{DB_FILE}'")
        print(f"详细信息：{e}")
        return

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"数据已导出到 {OUTPUT_FILE}")
    print(f"- 地图尺寸记录：{len(data['map_sizes'])} 天")
    print(f"- 玩家统计类型：{len(data['player_stats'])} 种")
    print(f"- 战斗统计类别：{len(data['battle_stats'])} 种")
    print(f"- 物品合成类别：{len(data['craft_stats'])} 种")
    print(f"- 物品统计类别：{len(data['item_stats'])} 种")

    # 显示日期范围
    dates = sorted(data['map_sizes'].keys())
    if dates:
        print(f"- 日期范围：{dates[0]} 至 {dates[-1]}")


if __name__ == '__main__':
    main()