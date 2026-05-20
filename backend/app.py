import atexit

from flask import Flask, send_from_directory

from backend.routes.api import api_bp
from backend.services.scheduler import start_scheduler, shutdown_scheduler


def create_app() -> Flask:
    app = Flask(__name__)

    app.register_blueprint(api_bp)

    @app.route('/')
    def index():
        return 'MineTrack API Server'

    start_scheduler()
    atexit.register(shutdown_scheduler)

    return app
