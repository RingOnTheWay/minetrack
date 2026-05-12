import os
import json
import sqlite3
import sys
import subprocess
from datetime import datetime

from flask import Blueprint, request, jsonify

from backend.config import DB_FILE, DATA_JSON
from backend.database.repositories import (
    get_connection,
    MapSizeRepository,
    PlayerStatsRepository,
    DetailStatsRepository,
)
from backend.services.scanner import scan_server_folder, batch_scan_parent_folder

api_bp = Blueprint('api', __name__)


@api_bp.route('/api/scan', methods=['POST'])
def scan_data():
    data = request.json
    server_folder = data.get('folder')
    date = data.get('date', datetime.now().strftime('%Y-%m-%d'))

    if not server_folder or not os.path.exists(server_folder):
        return jsonify({'error': '服务器文件夹不存在'}), 400

    try:
        result = scan_server_folder(server_folder, date)
        return jsonify({
            'success': True,
            'date': date,
            'maps': result['maps'],
            'player_count': result['player_count'],
            'battle_stats_count': result['battle_stats_count'],
            'craft_stats_count': result['craft_stats_count'],
            'item_stats_count': result['item_stats_count'],
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/api/map_sizes', methods=['GET'])
def get_map_sizes():
    return jsonify(MapSizeRepository.get_all())


@api_bp.route('/api/player_stats', methods=['GET'])
def get_player_stats():
    stat_type = request.args.get('type', 'play_time')
    return jsonify(PlayerStatsRepository.get_by_type(stat_type))


@api_bp.route('/api/stats/<stat_domain>', methods=['GET'])
def get_detail_stats(stat_domain: str):
    category = request.args.get('category')
    if not category:
        return jsonify({'error': '需要 category 参数'}), 400

    data = DetailStatsRepository.get_by_domain_and_category(stat_domain, category)
    return jsonify(data)


@api_bp.route('/api/stats/<stat_domain>/summary', methods=['GET'])
def get_detail_summary(stat_domain: str):
    category = request.args.get('category', 'killed')
    limit = int(request.args.get('limit', 10))
    data = DetailStatsRepository.get_summary(stat_domain, category, limit)
    return jsonify(data)


@api_bp.route('/api/battle_stats', methods=['GET'])
def get_battle_stats():
    category = request.args.get('category', 'killed')
    data = DetailStatsRepository.get_by_domain_and_category('battle', category)
    return jsonify(data)


@api_bp.route('/api/craft_stats', methods=['GET'])
def get_craft_stats():
    category = request.args.get('category', 'crafted')
    data = DetailStatsRepository.get_by_domain_and_category('craft', category)
    return jsonify(data)


@api_bp.route('/api/item_stats', methods=['GET'])
def get_item_stats():
    category = request.args.get('category', 'picked_up')
    data = DetailStatsRepository.get_by_domain_and_category('item', category)
    return jsonify(data)


@api_bp.route('/api/battle_summary', methods=['GET'])
def get_battle_summary():
    category = request.args.get('category', 'killed')
    limit = int(request.args.get('limit', 10))
    data = DetailStatsRepository.get_summary('battle', category, limit)
    return jsonify(data)


@api_bp.route('/api/dates', methods=['GET'])
def get_dates():
    dates = MapSizeRepository.get_distinct_dates()
    return jsonify(dates)


@api_bp.route('/api/delete_date', methods=['DELETE'])
def delete_date():
    data = request.json
    date = data.get('date')

    if not date:
        return jsonify({'error': '请提供日期'}), 400

    conn = get_connection()

    map_deleted = MapSizeRepository.delete_by_date(date, conn)
    player_deleted = PlayerStatsRepository.delete_by_date(date, conn)
    detail_deleted = DetailStatsRepository.delete_by_date(date, conn)

    conn.commit()
    conn.close()

    return jsonify({
        'success': True,
        'date': date,
        'map_records_deleted': map_deleted,
        'player_records_deleted': player_deleted,
        'detail_records_deleted': detail_deleted,
    })


@api_bp.route('/api/batch_delete', methods=['DELETE'])
def batch_delete():
    data = request.json
    dates = data.get('dates', [])

    if not dates:
        return jsonify({'error': '请提供日期列表'}), 400

    conn = get_connection()
    results = []
    total_map = 0
    total_player = 0
    total_detail = 0

    for date in dates:
        map_deleted = MapSizeRepository.delete_by_date(date, conn)
        player_deleted = PlayerStatsRepository.delete_by_date(date, conn)
        detail_deleted = DetailStatsRepository.delete_by_date(date, conn)

        total_map += map_deleted
        total_player += player_deleted
        total_detail += detail_deleted

        results.append({
            'date': date,
            'map_deleted': map_deleted,
            'player_deleted': player_deleted,
            'detail_deleted': detail_deleted,
        })

    conn.commit()
    conn.close()

    return jsonify({
        'success': True,
        'total_dates': len(dates),
        'total_map_deleted': total_map,
        'total_player_deleted': total_player,
        'total_detail_deleted': total_detail,
        'results': results,
    })


@api_bp.route('/api/export', methods=['POST'])
def export_data():
    try:
        result = subprocess.run(
            [sys.executable, 'scripts/export_data.py'],
            capture_output=True,
            text=True,
            cwd=os.path.join(os.path.dirname(os.path.dirname(__file__)), '..')
        )
        if result.returncode == 0:
            return jsonify({'success': True, 'message': '数据已导出'})
        else:
            return jsonify({'success': False, 'error': result.stderr}), 500
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@api_bp.route('/api/batch_scan', methods=['POST'])
def batch_scan():
    data = request.json
    parent_folder = data.get('parent_folder')

    if not parent_folder or not os.path.exists(parent_folder):
        return jsonify({'error': '父文件夹不存在'}), 400

    result = batch_scan_parent_folder(parent_folder)
    if 'error' in result:
        return jsonify(result), 500
    return jsonify(result)