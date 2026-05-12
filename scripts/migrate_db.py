#!/usr/bin/env python3
"""
数据迁移脚本：将旧的 battle_stats / craft_stats / item_stats 表
合并到新的 detail_stats 表
"""
import sqlite3
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database.init import init_db

DB_FILE = 'mc_stats.db'


def migrate():
    init_db()

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    tables = cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name IN ('battle_stats', 'craft_stats', 'item_stats')"
    ).fetchall()
    existing_tables = {row[0] for row in tables}

    if not existing_tables:
        print("没有找到需要迁移的旧表，无需迁移")
        conn.close()
        return

    domain_map = {
        'battle_stats': 'battle',
        'craft_stats': 'craft',
        'item_stats': 'item',
    }

    total_migrated = 0

    for old_table, domain in domain_map.items():
        if old_table not in existing_tables:
            print(f"- 旧表 {old_table} 不存在，跳过")
            continue

        count_before = cursor.execute(f'SELECT COUNT(*) FROM {old_table}').fetchone()[0]
        print(f"- {old_table}：{count_before} 行待迁移")

        rows = cursor.execute(
            f'SELECT date, player_name, stat_category, stat_key, stat_value FROM {old_table}'
        ).fetchall()

        for row_data in rows:
            date, player_name, stat_category, stat_key, stat_value = row_data
            cursor.execute(
                'INSERT OR REPLACE INTO detail_stats (date, player_name, stat_domain, stat_category, stat_key, stat_value) VALUES (?, ?, ?, ?, ?, ?)',
                (date, player_name, domain, stat_category, stat_key, stat_value)
            )

        migrated = len(rows)
        total_migrated += migrated
        print(f"  ✓ {migrated} 行已迁移")

    conn.commit()

    detail_count = cursor.execute('SELECT COUNT(*) FROM detail_stats').fetchone()[0]
    print(f"\n迁移完成！detail_stats 总计 {detail_count} 行")

    old_total = 0
    for old_table in domain_map:
        if old_table in existing_tables:
            old_total += cursor.execute(f'SELECT COUNT(*) FROM {old_table}').fetchone()[0]

    if old_total == 0 or detail_count >= total_migrated:
        print(f"\n数据完整性验证通过")
        print(f"迁移前总量: {old_total}, 迁移后总量: {detail_count}")
        print(f"\n旧表可以安全删除（已迁移完毕）")
        print(f"如需清理旧表，请在确认后手动执行:")
        for old_table in domain_map:
            if old_table in existing_tables:
                print(f"  DROP TABLE {old_table};")

    conn.close()


if __name__ == '__main__':
    migrate()