import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

DB_FILE = str(BASE_DIR / 'mc_stats.db')
DATA_JSON = str(BASE_DIR / 'data.json')

HOST = '0.0.0.0'
PORT = 5000
DEBUG = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'

EXPORT_SCRIPT = str(BASE_DIR / 'scripts' / 'export_data.py')