import sqlite3
from backend.config import DB_FILE

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute('PRAGMA journal_mode=WAL')

    # Migration: check if server_name column exists in map_sizes
    # If not, drop all old tables and recreate (development phase, data loss OK)
    cursor.execute("PRAGMA table_info(map_sizes)")
    columns = [col[1] for col in cursor.fetchall()]
    if 'server_name' not in columns:
        # Old schema without server_name - drop and recreate
        cursor.execute('DROP TABLE IF EXISTS map_sizes')
        cursor.execute('DROP TABLE IF EXISTS player_stats')
        cursor.execute('DROP TABLE IF EXISTS detail_stats')
        cursor.execute('DROP TABLE IF EXISTS servers')

    # Migration: check if sort_order column exists in servers
    cursor.execute("PRAGMA table_info(servers)")
    server_columns = [col[1] for col in cursor.fetchall()]
    if server_columns and 'sort_order' not in server_columns:
        cursor.execute('DROP TABLE IF EXISTS servers')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS servers (
            name TEXT PRIMARY KEY,
            sort_order INTEGER NOT NULL DEFAULT 0
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS map_sizes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            server_name TEXT NOT NULL DEFAULT 'default',
            date TEXT NOT NULL,
            map_name TEXT NOT NULL,
            size_mb REAL NOT NULL,
            UNIQUE(server_name, date, map_name)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS player_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            server_name TEXT NOT NULL DEFAULT 'default',
            date TEXT NOT NULL,
            player_name TEXT NOT NULL,
            stat_type TEXT NOT NULL,
            stat_value INTEGER NOT NULL,
            UNIQUE(server_name, date, player_name, stat_type)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS detail_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            server_name TEXT NOT NULL DEFAULT 'default',
            date TEXT NOT NULL,
            player_name TEXT NOT NULL,
            stat_domain TEXT NOT NULL,
            stat_category TEXT NOT NULL,
            stat_key TEXT NOT NULL,
            stat_value INTEGER NOT NULL,
            UNIQUE(server_name, date, player_name, stat_domain, stat_category, stat_key)
        )
    ''')

    conn.commit()
    conn.close()
    print("数据库初始化完成（WAL 模式）")
