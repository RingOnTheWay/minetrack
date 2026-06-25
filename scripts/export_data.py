#!/usr/bin/env python3
"""
导出数据库数据为 JSON 格式，供静态页面使用
使用方法：uv run python scripts/export_data.py
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database.init import init_db
from backend.services.exporter import export_to_json


def main():
    print("正在导出数据...")
    try:
        init_db()
        export_to_json()
    except Exception as e:
        print(f"错误：无法读取数据库")
        print(f"详细信息：{e}")


if __name__ == '__main__':
    main()