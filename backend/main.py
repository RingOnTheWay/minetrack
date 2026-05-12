import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.config import HOST, PORT, DEBUG
from backend.database.init import init_db
from backend.app import create_app


def main():
    init_db()

    app = create_app()
    app.debug = DEBUG

    print(f"MC Stats API 服务器启动在 http://{HOST}:{PORT}")
    app.run(host=HOST, port=PORT, debug=DEBUG)


if __name__ == '__main__':
    main()