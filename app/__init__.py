from flask import Flask

from .config import Config
from .extensions import db, migrate


def create_app():
    app = Flask(__name__)

    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    # Register models
    from app import models

    # Register Blueprints
    from app.views import main_bp as main_bp
    from app.api import bp as api_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix="/api/v1")

    return app
