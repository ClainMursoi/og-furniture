import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Use absolute import (more stable in VS Code)
from app.config import Config

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # Create upload folder if it doesn't exist
    if app.config.get('UPLOAD_FOLDER'):
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Register Blueprints
    from app.routes.customer import customer_bp
    from app.routes.admin import admin_bp

    app.register_blueprint(customer_bp)
    app.register_blueprint(admin_bp)

    return app