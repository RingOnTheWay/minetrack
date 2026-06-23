import os
from datetime import datetime, timedelta

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from backend.services.scanner import scan_server_folder
from backend.database.repositories import get_connection

_scheduler: BackgroundScheduler | None = None
_auto_scan_config: dict = {
    'enabled': False,
    'folder': '',
    'server_name': '',
}
_last_scan_status: dict = {
    'last_scan_time': None,
    'last_scan_success': None,
    'last_scan_date': None,
    'last_scan_error': None,
    'last_scan_result': None,
}


def get_auto_scan_config() -> dict:
    return dict(_auto_scan_config)


def update_auto_scan_config(enabled: bool | None = None, folder: str | None = None,
                            server_name: str | None = None) -> dict:
    global _auto_scan_config
    if enabled is not None:
        _auto_scan_config['enabled'] = enabled
    if folder is not None:
        _auto_scan_config['folder'] = folder
    if server_name is not None:
        _auto_scan_config['server_name'] = server_name

    if _scheduler:
        if _auto_scan_config['enabled'] and _auto_scan_config['folder']:
            _ensure_job()
        else:
            _remove_job()

    return dict(_auto_scan_config)


def get_last_scan_status() -> dict:
    return dict(_last_scan_status)


def _execute_auto_scan():
    global _last_scan_status
    folder = _auto_scan_config.get('folder', '')
    server_name = _auto_scan_config.get('server_name', '') or 'default'
    if not folder or not os.path.exists(folder):
        _last_scan_status = {
            'last_scan_time': datetime.now().isoformat(),
            'last_scan_success': False,
            'last_scan_date': None,
            'last_scan_error': f'文件夹不存在: {folder}',
            'last_scan_result': None,
        }
        return

    now = datetime.now()
    scan_date = (now - timedelta(seconds=1)).strftime('%Y-%m-%d')

    try:
        result = scan_server_folder(folder, date=scan_date, server_name=server_name)
        _last_scan_status = {
            'last_scan_time': now.isoformat(),
            'last_scan_success': True,
            'last_scan_date': result['date'],
            'last_scan_error': None,
            'last_scan_result': {
                'player_count': result['player_count'],
                'battle_stats_count': result['battle_stats_count'],
                'craft_stats_count': result['craft_stats_count'],
                'item_stats_count': result['item_stats_count'],
                'block_stats_count': result.get('block_stats_count', 0),
            },
        }
        print(f"[AutoScan] 扫描完成: date={result['date']} players={result['player_count']}")
    except Exception as e:
        _last_scan_status = {
            'last_scan_time': now.isoformat(),
            'last_scan_success': False,
            'last_scan_date': scan_date,
            'last_scan_error': str(e),
            'last_scan_result': None,
        }
        print(f"[AutoScan] 扫描失败: {e}")


def _ensure_job():
    if not _scheduler:
        return
    try:
        _scheduler.remove_job('auto_scan')
    except Exception:
        pass
    _scheduler.add_job(
        _execute_auto_scan,
        CronTrigger(hour=0, minute=0),
        id='auto_scan',
        replace_existing=True,
    )


def _remove_job():
    if not _scheduler:
        return
    try:
        _scheduler.remove_job('auto_scan')
    except Exception:
        pass


def start_scheduler():
    global _scheduler
    if _scheduler is not None:
        return
    _scheduler = BackgroundScheduler(daemon=True)
    _scheduler.start()
    if _auto_scan_config['enabled'] and _auto_scan_config['folder']:
        _ensure_job()
    print("[AutoScan] 定时调度器已启动")


def shutdown_scheduler():
    global _scheduler
    if _scheduler is None:
        return
    _remove_job()
    _scheduler.shutdown(wait=False)
    _scheduler = None
    print("[AutoScan] 定时调度器已停止")
