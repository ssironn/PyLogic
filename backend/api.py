#!/usr/bin/env python3
"""
PyLogic API - API REST para demonstracao de equivalencias logicas.

Este modulo fornece uma API REST usando APIFlask para verificar
equivalencia entre proposicoes logicas usando redes neurais.
"""
import os

from apiflask import APIFlask
from flask_cors import CORS
from dotenv import load_dotenv

from app.config import get_config
from app.extensions import db
from controller import register_blueprints
from commands import register_commands

# Import all models to ensure they are registered with SQLAlchemy
import models


# Load environment variables
load_dotenv()


def create_app(config_class=None):
    """Application factory."""
    app = APIFlask(
        __name__,
        title='PyLogic API',
        version='1.0.0',
        spec_path='/openapi.json',
        docs_ui='swagger-ui',
        docs_path='/docs'
    )

    # Load configuration
    if config_class is None:
        config_class = get_config()
    app.config.from_object(config_class)

    app.config['SPEC_FORMAT'] = 'json'
    app.config['AUTO_VALIDATION'] = True

    # Initialize extensions
    db.init_app(app)

    # Enable CORS for all origins
    CORS(app, resources={r"/*": {"origins": "*"}})

    # Register all blueprints via the main controller
    register_blueprints(app)

    # Register CLI commands
    register_commands(app)

    # Create database tables
    with app.app_context():
        db.create_all()

    return app


# Create the app instance
app = create_app()


if __name__ == '__main__':
    print("Iniciando PyLogic API...")

    # Pre-load models on startup (triggers the lazy loading in ProveService)
    with app.app_context():
        from resources.platform.prover.prove.service import _load_models
        _load_models()

    # Start the server
    app.run(host='0.0.0.0', port=5000, debug=True)
