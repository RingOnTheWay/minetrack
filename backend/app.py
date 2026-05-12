from flask import Flask, send_from_directory

from backend.routes.api import api_bp


def create_app() -> Flask:
    app = Flask(__name__)

    app.register_blueprint(api_bp)

    @app.route('/')
    def index():
        return 'MC Stats API Server'

    return app