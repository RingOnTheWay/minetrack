import os
import json
import sqlite3
import sys
import subprocess
from datetime import datetime

from flask import Blueprint, request, jsonify, Response

from backend.config import DB_FILE, DATA_JSON
from backend.database.repositories import (
    get_connection,
    MapSizeRepository,
    PlayerStatsRepository,
    DetailStatsRepository,
    ServerRepository,
)
from backend.services.scanner import (
    scan_server_folder, batch_scan_parent_folder, scan_archive,
    batch_scan_parent_folder_v2, _collect_scannable_items, _resolve_item_date,
    _parse_date_from_content, parse_date_from_folder_name,
    parse_date_from_server_properties,
)
from backend.services.archiver import is_archive_file, ARCHIVE_EXTENSIONS, ArchiveReader
from backend.services.parser import load_usercache_from_content, parse_all_stats_from_contents
from backend.services.scheduler import (
    get_auto_scan_config,
    update_auto_scan_config,
    get_last_scan_status,
    _execute_auto_scan,
)

api_bp = Blueprint('api', __name__)


# ==================== Server Management ====================

@api_bp.route('/api/servers', methods=['GET'])
def list_servers():
    servers = ServerRepository.get_all()
    return jsonify(servers)


@api_bp.route('/api/servers', methods=['POST'])
def add_server():
    data = request.json
    name = data.get('name', '').strip()
    if not name:
        return jsonify({'error': '服务器名称不能为空'}), 400
    try:
        ServerRepository.add(name)
        return jsonify({'success': True, 'name': name}), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 409


@api_bp.route('/api/servers/<name>', methods=['PUT'])
def rename_server(name: str):
    data = request.json
    new_name = data.get('new_name', '').strip()
    if not new_name:
        return jsonify({'error': '新服务器名称不能为空'}), 400
    try:
        ServerRepository.rename(name, new_name)
        return jsonify({'success': True, 'old_name': name, 'new_name': new_name})
    except ValueError as e:
        return jsonify({'error': str(e)}), 404


@api_bp.route('/api/servers/<name>', methods=['DELETE'])
def delete_server(name: str):
    try:
        ServerRepository.delete(name)
        return jsonify({'success': True, 'deleted_server': name})
    except ValueError as e:
        return jsonify({'error': str(e)}), 404


@api_bp.route('/api/servers/reorder', methods=['POST'])
def reorder_servers():
    data = request.json
    ordered_names = data.get('ordered_names', [])
    if not isinstance(ordered_names, list):
        return jsonify({'error': 'ordered_names 必须是数组'}), 400
    try:
        ServerRepository.reorder(ordered_names)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 400


# ==================== Browse ====================

@api_bp.route('/api/browse', methods=['GET'])
def browse_directory():
    path = request.args.get('path', '')
    if not path:
        if sys.platform == 'win32':
            drives = []
            for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
                drive = f'{letter}:\\'
                if os.path.exists(drive):
                    drives.append(drive)
            return jsonify({'path': '', 'parent': '', 'dirs': drives, 'is_root': True})
        else:
            path = '/'
    try:
        path = os.path.normpath(path)
        if not os.path.isdir(path):
            return jsonify({'error': '路径不是文件夹'}), 400
        parent = os.path.dirname(path)
        is_drive_root = False
        if sys.platform == 'win32':
            if len(path) == 3 and path[1] == ':' and path[2] == '\\':
                parent = '__root__'
                is_drive_root = True
        else:
            if path == '/':
                parent = ''
        entries = []
        archives = []
        for name in sorted(os.listdir(path)):
            full = os.path.join(path, name)
            if os.path.isdir(full):
                try:
                    os.listdir(full)
                    entries.append({'name': name, 'path': full, 'accessible': True, 'type': 'folder'})
                except PermissionError:
                    entries.append({'name': name, 'path': full, 'accessible': False, 'type': 'folder'})
            elif os.path.isfile(full) and is_archive_file(full):
                archives.append({'name': name, 'path': full, 'accessible': True, 'type': 'archive'})
        return jsonify({'path': path, 'parent': parent, 'dirs': entries, 'archives': archives, 'is_root': False})
    except PermissionError:
        return jsonify({'error': '无权限访问'}), 403
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== Scan ====================

@api_bp.route('/api/scan', methods=['POST'])
def scan_data():
    data = request.json
    server_folder = data.get('folder')

    if not server_folder or not os.path.exists(server_folder):
        return jsonify({'error': '服务器文件夹不存在'}), 400

    try:
        server_name = data.get('server_name', 'default')
        filter_config = data.get('filter_config', {})
        date = data.get('date') or None
        if date:
            import re
            if not re.match(r'^\d{4}-\d{2}-\d{2}$', date):
                return jsonify({'error': '日期格式无效，需为 YYYY-MM-DD'}), 400
        result = scan_server_folder(server_folder, date=date, server_name=server_name,
                                    filter_config=filter_config)
        response = {
            'success': True,
            'date': result['date'],
            'maps': result['maps'],
            'player_count': result['player_count'],
            'battle_stats_count': result['battle_stats_count'],
            'craft_stats_count': result['craft_stats_count'],
            'item_stats_count': result['item_stats_count'],
            'block_stats_count': result.get('block_stats_count', 0),
        }
        if result.get('filtered_count', 0) > 0:
            response['filtered_count'] = result['filtered_count']
            response['total_players'] = result['total_players']
        return jsonify(response)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/api/scan_archive', methods=['POST'])
def scan_archive_data():
    data = request.json
    archive_path = data.get('archive')

    if not archive_path or not os.path.exists(archive_path):
        return jsonify({'error': '压缩包文件不存在'}), 400

    if not is_archive_file(archive_path):
        return jsonify({'error': '不支持的压缩包格式'}), 400

    try:
        server_name = data.get('server_name', 'default')
        filter_config = data.get('filter_config', {})
        date = data.get('date') or None
        if date:
            import re
            if not re.match(r'^\d{4}-\d{2}-\d{2}$', date):
                return jsonify({'error': '日期格式无效，需为 YYYY-MM-DD'}), 400
        result = scan_archive(archive_path, date=date, server_name=server_name,
                              filter_config=filter_config)
        response = {
            'success': True,
            'date': result['date'],
            'maps': result['maps'],
            'player_count': result['player_count'],
            'battle_stats_count': result['battle_stats_count'],
            'craft_stats_count': result['craft_stats_count'],
            'item_stats_count': result['item_stats_count'],
            'block_stats_count': result.get('block_stats_count', 0),
        }
        if result.get('filtered_count', 0) > 0:
            response['filtered_count'] = result['filtered_count']
            response['total_players'] = result['total_players']
        return jsonify(response)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== Data Query ====================

@api_bp.route('/api/map_sizes', methods=['GET'])
def get_map_sizes():
    server_name = request.args.get('server_name')
    return jsonify(MapSizeRepository.get_all(server_name=server_name))


@api_bp.route('/api/player_stats', methods=['GET'])
def get_player_stats():
    stat_type = request.args.get('type', 'play_time')
    server_name = request.args.get('server_name')
    return jsonify(PlayerStatsRepository.get_by_type(stat_type, server_name=server_name))


@api_bp.route('/api/stats/<stat_domain>', methods=['GET'])
def get_detail_stats(stat_domain: str):
    category = request.args.get('category')
    if not category:
        return jsonify({'error': '需要 category 参数'}), 400

    server_name = request.args.get('server_name')
    data = DetailStatsRepository.get_by_domain_and_category(stat_domain, category,
                                                            server_name=server_name)
    return jsonify(data)


@api_bp.route('/api/stats/<stat_domain>/summary', methods=['GET'])
def get_detail_summary(stat_domain: str):
    category = request.args.get('category', 'killed')
    limit = int(request.args.get('limit', 10))
    server_name = request.args.get('server_name')
    data = DetailStatsRepository.get_summary(stat_domain, category, limit,
                                             server_name=server_name)
    return jsonify(data)


@api_bp.route('/api/battle_stats', methods=['GET'])
def get_battle_stats():
    category = request.args.get('category', 'killed')
    server_name = request.args.get('server_name')
    data = DetailStatsRepository.get_by_domain_and_category('battle', category,
                                                            server_name=server_name)
    return jsonify(data)


@api_bp.route('/api/craft_stats', methods=['GET'])
def get_craft_stats():
    category = request.args.get('category', 'crafted')
    server_name = request.args.get('server_name')
    data = DetailStatsRepository.get_by_domain_and_category('craft', category,
                                                            server_name=server_name)
    return jsonify(data)


@api_bp.route('/api/item_stats', methods=['GET'])
def get_item_stats():
    category = request.args.get('category', 'picked_up')
    server_name = request.args.get('server_name')
    data = DetailStatsRepository.get_by_domain_and_category('item', category,
                                                            server_name=server_name)
    return jsonify(data)


@api_bp.route('/api/block_stats', methods=['GET'])
def get_block_stats():
    category = request.args.get('category', 'mined')
    server_name = request.args.get('server_name')
    data = DetailStatsRepository.get_by_domain_and_category('block', category,
                                                            server_name=server_name)
    return jsonify(data)


@api_bp.route('/api/block_summary', methods=['GET'])
def get_block_summary():
    category = request.args.get('category', 'mined')
    limit = int(request.args.get('limit', 10))
    server_name = request.args.get('server_name')
    data = DetailStatsRepository.get_summary('block', category, limit,
                                             server_name=server_name)
    return jsonify(data)


@api_bp.route('/api/battle_summary', methods=['GET'])
def get_battle_summary():
    category = request.args.get('category', 'killed')
    limit = int(request.args.get('limit', 10))
    server_name = request.args.get('server_name')
    data = DetailStatsRepository.get_summary('battle', category, limit,
                                             server_name=server_name)
    return jsonify(data)


@api_bp.route('/api/dates', methods=['GET'])
def get_dates():
    server_name = request.args.get('server_name')
    dates = MapSizeRepository.get_distinct_dates(server_name=server_name)
    return jsonify(dates)


# ==================== Delete ====================

@api_bp.route('/api/delete_date', methods=['DELETE'])
def delete_date():
    data = request.json
    date = data.get('date')
    server_name = data.get('server_name')

    if not date:
        return jsonify({'error': '请提供日期'}), 400

    conn = get_connection()

    map_deleted = MapSizeRepository.delete_by_date(date, server_name=server_name, conn=conn)
    player_deleted = PlayerStatsRepository.delete_by_date(date, server_name=server_name, conn=conn)
    detail_deleted = DetailStatsRepository.delete_by_date(date, server_name=server_name, conn=conn)

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
    server_name = data.get('server_name')

    if not dates:
        return jsonify({'error': '请提供日期列表'}), 400

    conn = get_connection()
    results = []
    total_map = 0
    total_player = 0
    total_detail = 0

    for date in dates:
        map_deleted = MapSizeRepository.delete_by_date(date, server_name=server_name, conn=conn)
        player_deleted = PlayerStatsRepository.delete_by_date(date, server_name=server_name, conn=conn)
        detail_deleted = DetailStatsRepository.delete_by_date(date, server_name=server_name, conn=conn)

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


@api_bp.route('/api/delete_all', methods=['DELETE'])
def delete_all():
    data = request.json or {}
    server_name = data.get('server_name')

    conn = get_connection()
    cursor = conn.cursor()

    if server_name:
        cursor.execute('SELECT COUNT(*) FROM map_sizes WHERE server_name = ?', (server_name,))
        map_count = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(*) FROM player_stats WHERE server_name = ?', (server_name,))
        player_count = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(*) FROM detail_stats WHERE server_name = ?', (server_name,))
        detail_count = cursor.fetchone()[0]
        cursor.execute('DELETE FROM map_sizes WHERE server_name = ?', (server_name,))
        cursor.execute('DELETE FROM player_stats WHERE server_name = ?', (server_name,))
        cursor.execute('DELETE FROM detail_stats WHERE server_name = ?', (server_name,))
    else:
        cursor.execute('SELECT COUNT(*) FROM map_sizes')
        map_count = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(*) FROM player_stats')
        player_count = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(*) FROM detail_stats')
        detail_count = cursor.fetchone()[0]
        cursor.execute('DELETE FROM map_sizes')
        cursor.execute('DELETE FROM player_stats')
        cursor.execute('DELETE FROM detail_stats')

    conn.commit()
    conn.close()

    return jsonify({
        'success': True,
        'total_map_deleted': map_count,
        'total_player_deleted': player_count,
        'total_detail_deleted': detail_count,
    })


# ==================== Export ====================

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


# ==================== Batch Scan ====================

@api_bp.route('/api/batch_scan', methods=['POST'])
def batch_scan():
    data = request.json
    parent_folder = data.get('parent_folder')

    if not parent_folder or not os.path.exists(parent_folder):
        return jsonify({'error': '父文件夹不存在'}), 400

    server_name = data.get('server_name', 'default')
    filter_config = data.get('filter_config', {})
    result = batch_scan_parent_folder(parent_folder, server_name=server_name,
                                      filter_config=filter_config)
    if 'error' in result:
        return jsonify(result), 500
    return jsonify(result)


@api_bp.route('/api/list_scannable', methods=['POST'])
def list_scannable():
    data = request.json
    parent_folder = data.get('parent_folder')

    if not parent_folder or not os.path.exists(parent_folder):
        return jsonify({'error': '父文件夹不存在'}), 400

    from datetime import datetime

    items = _collect_scannable_items(parent_folder)
    folders = []
    for item in items:
        try:
            date = _resolve_item_date(item)
        except Exception:
            mtime = os.path.getmtime(item['path'])
            date = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d')
        folders.append({'folder': item['path'], 'date': date, 'name': item['name'], 'type': item['type']})

    return jsonify({'folders': folders, 'total': len(folders)})


@api_bp.route('/api/batch_scan_stream', methods=['POST'])
def batch_scan_stream():
    import json as _json

    data = request.json
    parent_folder = data.get('parent_folder')

    if not parent_folder or not os.path.exists(parent_folder):
        return jsonify({'error': '父文件夹不存在'}), 400

    server_name = data.get('server_name', 'default')
    filter_config = data.get('filter_config', {})
    scan_mode = data.get('scan_mode', 'folder')

    def generate():
        items = _collect_scannable_items(parent_folder)
        if scan_mode == 'folder':
            items = [it for it in items if it['type'] == 'folder']
        elif scan_mode == 'archive':
            items = [it for it in items if it['type'] == 'archive']
        total = len(items)
        yield f"data: {_json.dumps({'type': 'start', 'total': total})}\n\n"

        conn = get_connection()
        imported = 0
        filtered_count = 0
        errors = []

        for i, item in enumerate(items):
            try:
                if item['type'] == 'archive':
                    yield f"data: {_json.dumps({'type': 'extracting', 'current': i + 1, 'total': total, 'name': item['name'], 'item_type': 'archive'})}\n\n"

                    reader = ArchiveReader(item['path'])
                    for _ in reader.read_needed_gen():
                        pass

                    archive_data = reader.needed_data
                    if not archive_data or not archive_data.get('server_properties'):
                        raise ValueError('压缩包内未找到 server.properties')

                    try:
                        date = _parse_date_from_content(archive_data['server_properties'])
                    except ValueError:
                        try:
                            date = parse_date_from_folder_name(item['name'])
                        except ValueError:
                            mtime = os.path.getmtime(item['path'])
                            date = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d')

                    uuid_to_name = {}
                    if archive_data.get('usercache'):
                        uuid_to_name = load_usercache_from_content(archive_data['usercache'])

                    map_sizes = reader.compute_map_sizes()
                    stats_contents = archive_data.get('stats', {})

                    result = scan_server_folder(
                        '', date=date, server_name=server_name,
                        filter_config=filter_config, conn=conn,
                        map_sizes_override=map_sizes,
                        usercache_override=uuid_to_name,
                        stats_contents_override=stats_contents,
                    )
                else:
                    yield f"data: {_json.dumps({'type': 'progress', 'current': i + 1, 'total': total, 'name': item['name'], 'item_type': 'folder'})}\n\n"

                    try:
                        date = parse_date_from_server_properties(item['path'])
                    except ValueError:
                        try:
                            date = parse_date_from_folder_name(item['name'])
                        except ValueError:
                            mtime = os.path.getmtime(item['path'])
                            date = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d')

                    result = scan_server_folder(item['path'], date=date,
                                                server_name=server_name,
                                                filter_config=filter_config, conn=conn)

                if result.get('filtered_count', 0) > 0:
                    filtered_count += result['filtered_count']
                imported += 1
                if (i + 1) % 5 == 0 or i == total - 1:
                    conn.commit()
            except Exception as e:
                errors.append({'folder': item['name'], 'error': str(e)})

        conn.close()

        yield f"data: {_json.dumps({'type': 'complete', 'imported': imported, 'total': total, 'filtered_count': filtered_count, 'errors': errors})}\n\n"

    return Response(generate(), mimetype='text/event-stream', headers={
        'Cache-Control': 'no-cache',
        'X-Accel-Buffering': 'no',
    })


# ==================== Auto Scan ====================

@api_bp.route('/api/auto_scan/config', methods=['GET'])
def get_auto_scan_config_api():
    config = get_auto_scan_config()
    status = get_last_scan_status()
    return jsonify({
        'enabled': config['enabled'],
        'folder': config['folder'],
        'server_name': config.get('server_name', ''),
        'last_scan_time': status['last_scan_time'],
        'last_scan_success': status['last_scan_success'],
        'last_scan_date': status['last_scan_date'],
        'last_scan_error': status['last_scan_error'],
        'last_scan_result': status['last_scan_result'],
    })


@api_bp.route('/api/auto_scan/config', methods=['POST'])
def update_auto_scan_config_api():
    data = request.json
    enabled = data.get('enabled')
    folder = data.get('folder')
    server_name = data.get('server_name')

    if enabled is not None and not isinstance(enabled, bool):
        return jsonify({'error': 'enabled 必须为布尔值'}), 400
    if folder is not None and not isinstance(folder, str):
        return jsonify({'error': 'folder 必须为字符串'}), 400
    if server_name is not None and not isinstance(server_name, str):
        return jsonify({'error': 'server_name 必须为字符串'}), 400

    if enabled is True and folder is not None and folder.strip():
        if not os.path.exists(folder.strip()):
            return jsonify({'error': '指定的文件夹路径不存在'}), 400

    config = update_auto_scan_config(enabled=enabled, folder=folder, server_name=server_name)
    return jsonify({
        'success': True,
        'enabled': config['enabled'],
        'folder': config['folder'],
        'server_name': config.get('server_name', ''),
    })


@api_bp.route('/api/auto_scan/trigger', methods=['POST'])
def trigger_auto_scan():
    config = get_auto_scan_config()
    if not config['enabled']:
        return jsonify({'error': '自动扫描未启用'}), 400
    if not config['folder'] or not os.path.exists(config['folder']):
        return jsonify({'error': '未配置有效的扫描文件夹'}), 400

    try:
        _execute_auto_scan()
        status = get_last_scan_status()
        if status['last_scan_success']:
            return jsonify({
                'success': True,
                'date': status['last_scan_date'],
                'result': status['last_scan_result'],
            })
        else:
            return jsonify({'success': False, 'error': status['last_scan_error']}), 500
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@api_bp.route('/api/batch_delete_stream', methods=['POST'])
def batch_delete_stream():
    import json as _json

    data = request.json
    dates_to_delete = data.get('dates', [])
    server_name = data.get('server_name')

    if not dates_to_delete:
        return jsonify({'error': '请提供日期列表'}), 400

    def generate():
        total = len(dates_to_delete)
        yield f"data: {_json.dumps({'type': 'start', 'total': total})}\n\n"

        conn = get_connection()
        total_map = 0
        total_player = 0
        total_detail = 0
        success_count = 0

        for i, date in enumerate(dates_to_delete):
            yield f"data: {_json.dumps({'type': 'progress', 'current': i + 1, 'total': total, 'date': date})}\n\n"

            map_deleted = MapSizeRepository.delete_by_date(date, server_name=server_name, conn=conn)
            player_deleted = PlayerStatsRepository.delete_by_date(date, server_name=server_name, conn=conn)
            detail_deleted = DetailStatsRepository.delete_by_date(date, server_name=server_name, conn=conn)

            total_map += map_deleted
            total_player += player_deleted
            total_detail += detail_deleted
            success_count += 1

            if (i + 1) % 10 == 0 or i == total - 1:
                conn.commit()

        conn.close()

        yield f"data: {_json.dumps({'type': 'complete', 'total_dates': success_count, 'total_map_deleted': total_map, 'total_player_deleted': total_player, 'total_detail_deleted': total_detail})}\n\n"

    return Response(generate(), mimetype='text/event-stream', headers={
        'Cache-Control': 'no-cache',
        'X-Accel-Buffering': 'no',
    })
