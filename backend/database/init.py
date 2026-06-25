import sqlite3
from backend.config import DB_FILE

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute('PRAGMA journal_mode=WAL')

    # Migration: add server_name column to existing tables if missing
    for table in ['map_sizes', 'player_stats', 'detail_stats']:
        cursor.execute(f"PRAGMA table_info({table})")
        columns = [col[1] for col in cursor.fetchall()]
        if columns and 'server_name' not in columns:
            # Preserve existing data by adding column with default value
            cursor.execute(f"ALTER TABLE {table} ADD COLUMN server_name TEXT NOT NULL DEFAULT 'default'")
            # Recreate UNIQUE index to include server_name
            # SQLite doesn't support ALTER INDEX, so we recreate the table
            _rebuild_table_with_server_name(cursor, table, columns)

    # Migration: add sort_order column to servers if missing
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


def _rebuild_table_with_server_name(cursor, table: str, old_columns: list[str]):
    """Rebuild a table to include server_name in the UNIQUE constraint.
    This preserves existing data by copying it to a new table."""
    # Map old table -> new table definition
    table_defs = {
        'map_sizes': '''
            CREATE TABLE map_sizes_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                server_name TEXT NOT NULL DEFAULT 'default',
                date TEXT NOT NULL,
                map_name TEXT NOT NULL,
                size_mb REAL NOT NULL,
                UNIQUE(server_name, date, map_name)
            )
        ''',
        'player_stats': '''
            CREATE TABLE player_stats_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                server_name TEXT NOT NULL DEFAULT 'default',
                date TEXT NOT NULL,
                player_name TEXT NOT NULL,
                stat_type TEXT NOT NULL,
                stat_value INTEGER NOT NULL,
                UNIQUE(server_name, date, player_name, stat_type)
            )
        ''',
        'detail_stats': '''
            CREATE TABLE detail_stats_new (
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
        ''',
    }

    if table not in table_defs:
        return

    col_list = ', '.join(old_columns)
    cursor.execute(table_defs[table])
    cursor.execute(f'INSERT INTO {table}_new ({col_list}) SELECT {col_list} FROM {table}')
    cursor.execute(f'DROP TABLE {table}')
    cursor.execute(f'ALTER TABLE {table}_new RENAME TO {table}')
