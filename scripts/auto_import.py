#!/usr/bin/env python3
import sys
import os
import json
import urllib.request
import urllib.error
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

API_URL = "http://localhost:5000/api/scan"
API_TIMEOUT = 15


def try_api_import(server_folder: str, date: str) -> bool:
    try:
        payload = json.dumps({
            "folder": server_folder,
            "date": date,
            "filter_config": {},
        }).encode("utf-8")
        req = urllib.request.Request(
            API_URL,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=API_TIMEOUT) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            if result.get("success"):
                print(f"  [API] date={result.get('date')}  players={result.get('player_count')}  "
                      f"battle={result.get('battle_stats_count')}  craft={result.get('craft_stats_count')}  "
                      f"item={result.get('item_stats_count')}  block={result.get('block_stats_count', 0)}")
                return True
            else:
                print(f"  [API] returned error: {result.get('error', result)}")
                return False
    except urllib.error.URLError:
        print("  [API] backend not reachable, falling back to direct import")
        return False
    except Exception as e:
        print(f"  [API] exception: {e}")
        return False


def direct_import(server_folder: str, date: str) -> bool:
    try:
        from backend.database.init import init_db
        from backend.services.scanner import scan_server_folder

        init_db()
        result = scan_server_folder(server_folder, date=date)
        print(f"  [Direct] date={result['date']}  players={result['player_count']}  "
              f"battle={result['battle_stats_count']}  craft={result['craft_stats_count']}  "
              f"item={result['item_stats_count']}  block={result.get('block_stats_count', 0)}")
        return True
    except Exception as e:
        print(f"  [Direct] import failed: {e}")
        return False


def main():
    if len(sys.argv) < 2:
        print("Usage: uv run python scripts/auto_import.py <server_folder> [date]")
        sys.exit(1)

    server_folder = os.path.normpath(sys.argv[1])
    date = sys.argv[2] if len(sys.argv) >= 3 else datetime.now().strftime("%Y-%m-%d")

    if not os.path.isdir(server_folder):
        print(f"[MineTrack] Error: folder not found: {server_folder}")
        sys.exit(1)

    print(f"[MineTrack] Auto import: {server_folder}  date={date}")

    if not try_api_import(server_folder, date):
        if not direct_import(server_folder, date):
            print("[MineTrack] Import failed")
            sys.exit(1)

    print("[MineTrack] Import complete")


if __name__ == "__main__":
    main()
