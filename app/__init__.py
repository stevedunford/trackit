from flask import Flask, app

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
    from app.routes.home import bp as home_bp

    app.register_blueprint(home_bp)

    return app
