import sqlite3
from typing import Optional
from backend.config import DB_FILE

def get_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA journal_mode=WAL')
    return conn


class MapSizeRepository:
    @staticmethod
    def get_all():
        conn = get_connection()
        rows = conn.execute(
            'SELECT date, map_name, size_mb FROM map_sizes ORDER BY date, map_name'
        ).fetchall()
        conn.close()
        data = {}
        for row in rows:
            date, map_name, size_mb = row['date'], row['map_name'], row['size_mb']
            if date not in data:
                data[date] = {}
            data[date][map_name] = round(size_mb, 2)
        return data

    @staticmethod
    def insert_or_replace(date: str, map_name: str, size_mb: float, conn: Optional[sqlite3.Connection] = None):
        close_conn = conn is None
        if close_conn:
            conn = get_connection()
        conn.execute(
            'INSERT OR REPLACE INTO map_sizes (date, map_name, size_mb) VALUES (?, ?, ?)',
            (date, map_name, size_mb)
        )
        if close_conn:
            conn.commit()
            conn.close()

    @staticmethod
    def delete_by_date(date: str, conn: Optional[sqlite3.Connection] = None):
        close_conn = conn is None
        if close_conn:
            conn = get_connection()
        cursor = conn.execute('DELETE FROM map_sizes WHERE date = ?', (date,))
        deleted = cursor.rowcount
        if close_conn:
            conn.commit()
            conn.close()
        return deleted

    @staticmethod
    def get_distinct_dates() -> list[str]:
        conn = get_connection()
        rows = conn.execute('SELECT DISTINCT date FROM map_sizes ORDER BY date').fetchall()
        conn.close()
        return [row['date'] for row in rows]


class PlayerStatsRepository:
    @staticmethod
    def get_by_type(stat_type: str) -> dict:
        conn = get_connection()
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
    def get_all_types() -> list[str]:
        conn = get_connection()
        rows = conn.execute('SELECT DISTINCT stat_type FROM player_stats').fetchall()
        conn.close()
        return [row['stat_type'] for row in rows]

    @staticmethod
    def get_all() -> dict:
        conn = get_connection()
        stat_types = PlayerStatsRepository.get_all_types()
        result = {}
        for stat_type in stat_types:
            result[stat_type] = PlayerStatsRepository.get_by_type(stat_type)
        conn.close()
        return result

    @staticmethod
    def insert_or_replace(date: str, player_name: str, stat_type: str, stat_value: int,
                          conn: Optional[sqlite3.Connection] = None):
        close_conn = conn is None
        if close_conn:
            conn = get_connection()
        conn.execute(
            'INSERT OR REPLACE INTO player_stats (date, player_name, stat_type, stat_value) VALUES (?, ?, ?, ?)',
            (date, player_name, stat_type, stat_value)
        )
        if close_conn:
            conn.commit()
            conn.close()

    @staticmethod
    def delete_by_date(date: str, conn: Optional[sqlite3.Connection] = None):
        close_conn = conn is None
        if close_conn:
            conn = get_connection()
        cursor = conn.execute('DELETE FROM player_stats WHERE date = ?', (date,))
        deleted = cursor.rowcount
        if close_conn:
            conn.commit()
            conn.close()
        return deleted


class DetailStatsRepository:
    VALID_DOMAINS = {'battle', 'craft', 'item'}

    @staticmethod
    def get_by_domain_and_category(stat_domain: str, stat_category: str) -> dict:
        if stat_domain not in DetailStatsRepository.VALID_DOMAINS:
            return {}
        conn = get_connection()
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
    def get_all_by_domain(stat_domain: str) -> dict:
        if stat_domain not in DetailStatsRepository.VALID_DOMAINS:
            return {}
        conn = get_connection()
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
    def get_all() -> dict:
        result = {}
        for domain in DetailStatsRepository.VALID_DOMAINS:
            result[domain] = DetailStatsRepository.get_all_by_domain(domain)
        return result

    @staticmethod
    def get_summary(stat_domain: str, stat_category: str, limit: int = 10) -> dict:
        if stat_domain not in DetailStatsRepository.VALID_DOMAINS:
            return {'top_items': [], 'player_totals': []}
        conn = get_connection()

        top_items_rows = conn.execute(
            'SELECT stat_key, SUM(stat_value) as total FROM detail_stats WHERE stat_domain = ? AND stat_category = ? GROUP BY stat_key ORDER BY total DESC LIMIT ?',
            (stat_domain, stat_category, limit)
        ).fetchall()

        top_items = [{'name': row['stat_key'], 'total': row['total']} for row in top_items_rows]

        player_totals_rows = conn.execute(
            'SELECT player_name, SUM(stat_value) as total FROM detail_stats WHERE stat_domain = ? AND stat_category = ? GROUP BY player_name ORDER BY total DESC',
            (stat_domain, stat_category)
        ).fetchall()

        player_totals = [{'name': row['player_name'], 'total': row['total']} for row in player_totals_rows]

        conn.close()
        return {'top_items': top_items, 'player_totals': player_totals}

    @staticmethod
    def insert_or_replace(date: str, player_name: str, stat_domain: str, stat_category: str,
                          stat_key: str, stat_value: int, conn: Optional[sqlite3.Connection] = None):
        close_conn = conn is None
        if close_conn:
            conn = get_connection()
        conn.execute(
            'INSERT OR REPLACE INTO detail_stats (date, player_name, stat_domain, stat_category, stat_key, stat_value) VALUES (?, ?, ?, ?, ?, ?)',
            (date, player_name, stat_domain, stat_category, stat_key, stat_value)
        )
        if close_conn:
            conn.commit()
            conn.close()

    @staticmethod
    def delete_by_date(date: str, conn: Optional[sqlite3.Connection] = None):
        close_conn = conn is None
        if close_conn:
            conn = get_connection()
        cursor = conn.execute('DELETE FROM detail_stats WHERE date = ?', (date,))
        deleted = cursor.rowcount
        if close_conn:
            conn.commit()
            conn.close()
        return deleted