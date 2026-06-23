import sqlite3
import json
from typing import Optional
from backend.config import DB_FILE

def get_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA journal_mode=WAL')
    return conn


class ServerRepository:
    @staticmethod
    def get_all() -> list[str]:
        conn = get_connection()
        rows = conn.execute('SELECT name FROM servers ORDER BY sort_order, name').fetchall()
        conn.close()
        return [row['name'] for row in rows]

    @staticmethod
    def add(name: str):
        conn = get_connection()
        try:
            max_order = conn.execute('SELECT COALESCE(MAX(sort_order), -1) FROM servers').fetchone()[0]
            conn.execute('INSERT INTO servers (name, sort_order) VALUES (?, ?)', (name, max_order + 1))
            conn.commit()
        except sqlite3.IntegrityError:
            conn.close()
            raise ValueError(f'服务器名称 "{name}" 已存在')
        conn.close()

    @staticmethod
    def rename(old_name: str, new_name: str):
        conn = get_connection()
        try:
            existing = conn.execute('SELECT name FROM servers WHERE name = ?', (old_name,)).fetchone()
            if not existing:
                conn.close()
                raise ValueError(f'服务器 "{old_name}" 不存在')
            duplicate = conn.execute('SELECT name FROM servers WHERE name = ?', (new_name,)).fetchone()
            if duplicate:
                conn.close()
                raise ValueError(f'服务器名称 "{new_name}" 已存在')
            conn.execute('UPDATE servers SET name = ? WHERE name = ?', (new_name, old_name))
            conn.execute('UPDATE map_sizes SET server_name = ? WHERE server_name = ?', (new_name, old_name))
            conn.execute('UPDATE player_stats SET server_name = ? WHERE server_name = ?', (new_name, old_name))
            conn.execute('UPDATE detail_stats SET server_name = ? WHERE server_name = ?', (new_name, old_name))
            conn.commit()
        except Exception:
            conn.rollback()
            conn.close()
            raise
        conn.close()

    @staticmethod
    def delete(name: str):
        conn = get_connection()
        existing = conn.execute('SELECT name FROM servers WHERE name = ?', (name,)).fetchone()
        if not existing:
            conn.close()
            raise ValueError(f'服务器 "{name}" 不存在')
        conn.execute('DELETE FROM servers WHERE name = ?', (name,))
        conn.execute('DELETE FROM map_sizes WHERE server_name = ?', (name,))
        conn.execute('DELETE FROM player_stats WHERE server_name = ?', (name,))
        conn.execute('DELETE FROM detail_stats WHERE server_name = ?', (name,))
        conn.commit()
        conn.close()

    @staticmethod
    def exists(name: str) -> bool:
        conn = get_connection()
        row = conn.execute('SELECT name FROM servers WHERE name = ?', (name,)).fetchone()
        conn.close()
        return row is not None

    @staticmethod
    def reorder(ordered_names: list[str]):
        conn = get_connection()
        try:
            for i, name in enumerate(ordered_names):
                conn.execute('UPDATE servers SET sort_order = ? WHERE name = ?', (i, name))
            conn.commit()
        except Exception:
            conn.rollback()
            conn.close()
            raise
        conn.close()


class MapSizeRepository:
    @staticmethod
    def get_all(server_name: Optional[str] = None):
        conn = get_connection()
        if server_name:
            rows = conn.execute(
                'SELECT date, map_name, size_mb FROM map_sizes WHERE server_name = ? ORDER BY date, map_name',
                (server_name,)
            ).fetchall()
        else:
            rows = conn.execute(
                'SELECT server_name, date, map_name, size_mb FROM map_sizes ORDER BY server_name, date, map_name'
            ).fetchall()
        conn.close()
        data = {}
        for row in rows:
            if server_name:
                date, map_name, size_mb = row['date'], row['map_name'], row['size_mb']
            else:
                date, map_name, size_mb = row['date'], row['map_name'], row['size_mb']
            if date not in data:
                data[date] = {}
            data[date][map_name] = round(size_mb, 2)
        return data

    @staticmethod
    def insert_or_replace(server_name: str, date: str, map_name: str, size_mb: float,
                          conn: Optional[sqlite3.Connection] = None):
        close_conn = conn is None
        if close_conn:
            conn = get_connection()
        conn.execute(
            'INSERT OR REPLACE INTO map_sizes (server_name, date, map_name, size_mb) VALUES (?, ?, ?, ?)',
            (server_name, date, map_name, size_mb)
        )
        if close_conn:
            conn.commit()
            conn.close()

    @staticmethod
    def insert_many(rows: list, conn: Optional[sqlite3.Connection] = None):
        close_conn = conn is None
        if close_conn:
            conn = get_connection()
        conn.executemany(
            'INSERT OR REPLACE INTO map_sizes (server_name, date, map_name, size_mb) VALUES (?, ?, ?, ?)',
            rows
        )
        if close_conn:
            conn.commit()
            conn.close()

    @staticmethod
    def delete_by_date(date: str, server_name: Optional[str] = None,
                       conn: Optional[sqlite3.Connection] = None):
        close_conn = conn is None
        if close_conn:
            conn = get_connection()
        if server_name:
            cursor = conn.execute('DELETE FROM map_sizes WHERE date = ? AND server_name = ?',
                                  (date, server_name))
        else:
            cursor = conn.execute('DELETE FROM map_sizes WHERE date = ?', (date,))
        deleted = cursor.rowcount
        if close_conn:
            conn.commit()
            conn.close()
        return deleted

    @staticmethod
    def get_distinct_dates(server_name: Optional[str] = None) -> list[str]:
        conn = get_connection()
        if server_name:
            rows = conn.execute(
                'SELECT DISTINCT date FROM map_sizes WHERE server_name = ? ORDER BY date',
                (server_name,)
            ).fetchall()
        else:
            rows = conn.execute('SELECT DISTINCT date FROM map_sizes ORDER BY date').fetchall()
        conn.close()
        return [row['date'] for row in rows]


class PlayerStatsRepository:
    @staticmethod
    def get_by_type(stat_type: str, server_name: Optional[str] = None) -> dict:
        conn = get_connection()
        if server_name:
            rows = conn.execute(
                'SELECT date, player_name, stat_value FROM player_stats WHERE stat_type = ? AND server_name = ? ORDER BY date, player_name',
                (stat_type, server_name)
            ).fetchall()
        else:
            rows = conn.execute(
                'SELECT date, player_name, stat_value FROM player_stats WHERE stat_type = ? ORDER BY date, player_name',
                (stat_type,)
            ).fetchall()
        conn.close()
        data = {}
        for row in rows:
            date, player_name, stat_value = row['date'], row['player_name'], row['stat_value']
            if date not in data:
                data[date] = {}
            data[date][player_name] = stat_value
        return data

    @staticmethod
    def get_all_types(server_name: Optional[str] = None) -> list[str]:
        conn = get_connection()
        if server_name:
            rows = conn.execute(
                'SELECT DISTINCT stat_type FROM player_stats WHERE server_name = ?',
                (server_name,)
            ).fetchall()
        else:
            rows = conn.execute('SELECT DISTINCT stat_type FROM player_stats').fetchall()
        conn.close()
        return [row['stat_type'] for row in rows]

    @staticmethod
    def get_all(server_name: Optional[str] = None) -> dict:
        stat_types = PlayerStatsRepository.get_all_types(server_name)
        result = {}
        for stat_type in stat_types:
            result[stat_type] = PlayerStatsRepository.get_by_type(stat_type, server_name)
        return result

    @staticmethod
    def insert_or_replace(server_name: str, date: str, player_name: str, stat_type: str,
                          stat_value: int, conn: Optional[sqlite3.Connection] = None):
        close_conn = conn is None
        if close_conn:
            conn = get_connection()
        conn.execute(
            'INSERT OR REPLACE INTO player_stats (server_name, date, player_name, stat_type, stat_value) VALUES (?, ?, ?, ?, ?)',
            (server_name, date, player_name, stat_type, stat_value)
        )
        if close_conn:
            conn.commit()
            conn.close()

    @staticmethod
    def insert_many(rows: list, conn: Optional[sqlite3.Connection] = None):
        close_conn = conn is None
        if close_conn:
            conn = get_connection()
        conn.executemany(
            'INSERT OR REPLACE INTO player_stats (server_name, date, player_name, stat_type, stat_value) VALUES (?, ?, ?, ?, ?)',
            rows
        )
        if close_conn:
            conn.commit()
            conn.close()

    @staticmethod
    def delete_by_date(date: str, server_name: Optional[str] = None,
                       conn: Optional[sqlite3.Connection] = None):
        close_conn = conn is None
        if close_conn:
            conn = get_connection()
        if server_name:
            cursor = conn.execute('DELETE FROM player_stats WHERE date = ? AND server_name = ?',
                                  (date, server_name))
        else:
            cursor = conn.execute('DELETE FROM player_stats WHERE date = ?', (date,))
        deleted = cursor.rowcount
        if close_conn:
            conn.commit()
            conn.close()
        return deleted


class DetailStatsRepository:
    VALID_DOMAINS = {'battle', 'craft', 'item', 'block'}

    @staticmethod
    def get_by_domain_and_category(stat_domain: str, stat_category: str,
                                   server_name: Optional[str] = None) -> dict:
        if stat_domain not in DetailStatsRepository.VALID_DOMAINS:
            return {}
        conn = get_connection()
        if server_name:
            rows = conn.execute(
                'SELECT date, player_name, stat_key, stat_value FROM detail_stats WHERE stat_domain = ? AND stat_category = ? AND server_name = ? ORDER BY date, player_name',
                (stat_domain, stat_category, server_name)
            ).fetchall()
        else:
            rows = conn.execute(
                'SELECT date, player_name, stat_key, stat_value FROM detail_stats WHERE stat_domain = ? AND stat_category = ? ORDER BY date, player_name',
                (stat_domain, stat_category)
            ).fetchall()
        conn.close()
        data = {}
        for row in rows:
            date, player_name, stat_key, stat_value = row['date'], row['player_name'], row['stat_key'], row['stat_value']
            if date not in data:
                data[date] = {}
            if player_name not in data[date]:
                data[date][player_name] = {}
            data[date][player_name][stat_key] = stat_value
        return data

    @staticmethod
    def get_all_by_domain(stat_domain: str, server_name: Optional[str] = None) -> dict:
        if stat_domain not in DetailStatsRepository.VALID_DOMAINS:
            return {}
        conn = get_connection()
        if server_name:
            rows = conn.execute(
                'SELECT date, player_name, stat_category, stat_key, stat_value FROM detail_stats WHERE stat_domain = ? AND server_name = ? ORDER BY date, player_name',
                (stat_domain, server_name)
            ).fetchall()
        else:
            rows = conn.execute(
                'SELECT date, player_name, stat_category, stat_key, stat_value FROM detail_stats WHERE stat_domain = ? ORDER BY date, player_name',
                (stat_domain,)
            ).fetchall()
        conn.close()
        data = {}
        for row in rows:
            date = row['date']
            player_name = row['player_name']
            stat_category = row['stat_category']
            stat_key = row['stat_key']
            stat_value = row['stat_value']
            if stat_category not in data:
                data[stat_category] = {}
            if date not in data[stat_category]:
                data[stat_category][date] = {}
            if player_name not in data[stat_category][date]:
                data[stat_category][date][player_name] = {}
            data[stat_category][date][player_name][stat_key] = stat_value
        return data

    @staticmethod
    def get_all(server_name: Optional[str] = None) -> dict:
        result = {}
        for domain in DetailStatsRepository.VALID_DOMAINS:
            result[domain] = DetailStatsRepository.get_all_by_domain(domain, server_name)
        return result

    @staticmethod
    def get_summary(stat_domain: str, stat_category: str, limit: int = 10,
                    server_name: Optional[str] = None) -> dict:
        if stat_domain not in DetailStatsRepository.VALID_DOMAINS:
            return {'top_items': [], 'player_totals': []}
        conn = get_connection()

        if server_name:
            top_items_rows = conn.execute(
                'SELECT stat_key, SUM(stat_value) as total FROM detail_stats WHERE stat_domain = ? AND stat_category = ? AND server_name = ? GROUP BY stat_key ORDER BY total DESC LIMIT ?',
                (stat_domain, stat_category, server_name, limit)
            ).fetchall()

            player_totals_rows = conn.execute(
                'SELECT player_name, SUM(stat_value) as total FROM detail_stats WHERE stat_domain = ? AND stat_category = ? AND server_name = ? GROUP BY player_name ORDER BY total DESC',
                (stat_domain, stat_category, server_name)
            ).fetchall()
        else:
            top_items_rows = conn.execute(
                'SELECT stat_key, SUM(stat_value) as total FROM detail_stats WHERE stat_domain = ? AND stat_category = ? GROUP BY stat_key ORDER BY total DESC LIMIT ?',
                (stat_domain, stat_category, limit)
            ).fetchall()

            player_totals_rows = conn.execute(
                'SELECT player_name, SUM(stat_value) as total FROM detail_stats WHERE stat_domain = ? AND stat_category = ? GROUP BY player_name ORDER BY total DESC',
                (stat_domain, stat_category)
            ).fetchall()

        top_items = [{'name': row['stat_key'], 'total': row['total']} for row in top_items_rows]

        player_totals = [{'name': row['player_name'], 'total': row['total']} for row in player_totals_rows]

        conn.close()
        return {'top_items': top_items, 'player_totals': player_totals}

    @staticmethod
    def insert_or_replace(server_name: str, date: str, player_name: str, stat_domain: str,
                          stat_category: str, stat_key: str, stat_value: int,
                          conn: Optional[sqlite3.Connection] = None):
        close_conn = conn is None
        if close_conn:
            conn = get_connection()
        conn.execute(
            'INSERT OR REPLACE INTO detail_stats (server_name, date, player_name, stat_domain, stat_category, stat_key, stat_value) VALUES (?, ?, ?, ?, ?, ?, ?)',
            (server_name, date, player_name, stat_domain, stat_category, stat_key, stat_value)
        )
        if close_conn:
            conn.commit()
            conn.close()

    @staticmethod
    def insert_many(rows: list, conn: Optional[sqlite3.Connection] = None):
        close_conn = conn is None
        if close_conn:
            conn = get_connection()
        conn.executemany(
            'INSERT OR REPLACE INTO detail_stats (server_name, date, player_name, stat_domain, stat_category, stat_key, stat_value) VALUES (?, ?, ?, ?, ?, ?, ?)',
            rows
        )
        if close_conn:
            conn.commit()
            conn.close()

    @staticmethod
    def delete_by_date(date: str, server_name: Optional[str] = None,
                       conn: Optional[sqlite3.Connection] = None):
        close_conn = conn is None
        if close_conn:
            conn = get_connection()
        if server_name:
            cursor = conn.execute('DELETE FROM detail_stats WHERE date = ? AND server_name = ?',
                                  (date, server_name))
        else:
            cursor = conn.execute('DELETE FROM detail_stats WHERE date = ?', (date,))
        deleted = cursor.rowcount
        if close_conn:
            conn.commit()
            conn.close()
        return deleted
