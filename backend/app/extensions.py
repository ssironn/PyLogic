"""
Flask extensions initialization.

This module initializes Flask extensions that are used across the application.
Extensions are initialized without an app instance and bound later using init_app().
"""
from flask_sqlalchemy import SQLAlchemy

# SQLAlchemy database instance
db = SQLAlchemy()
