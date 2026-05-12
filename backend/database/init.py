import sqlite3
from backend.config import DB_FILE

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute('PRAGMA journal_mode=WAL')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS map_sizes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            map_name TEXT NOT NULL,
            size_mb REAL NOT NULL,
            UNIQUE(date, map_name)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS player_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            player_name TEXT NOT NULL,
            stat_type TEXT NOT NULL,
            stat_value INTEGER NOT NULL,
            UNIQUE(date, player_name, stat_type)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS detail_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            player_name TEXT NOT NULL,
            stat_domain TEXT NOT NULL,
            stat_category TEXT NOT NULL,
            stat_key TEXT NOT NULL,
            stat_value INTEGER NOT NULL,
            UNIQUE(date, player_name, stat_domain, stat_category, stat_key)
        )
    ''')

    conn.commit()
    conn.close()
    print("数据库初始化完成（WAL 模式）")