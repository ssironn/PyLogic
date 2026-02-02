"""
Main controller that registers all API blueprints.

All endpoints in the application are registered through this module.
"""
from resources.admin.controller import admin_bp
from resources.platform.auth.controller import auth_bp
from resources.platform.courses.controller import courses_bp
from resources.platform.content.controller import content_bp
from resources.platform.profile.controller import profile_bp
from resources.platform.prover.controller import prover_bp
from resources.platform.questions.controller import questions_bp


def register_blueprints(app):
    """Registra todos os blueprints na aplicacao."""
    # Admin
    app.register_blueprint(admin_bp)

    # Platform
    app.register_blueprint(auth_bp)
    app.register_blueprint(courses_bp)
    app.register_blueprint(content_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(prover_bp)
    app.register_blueprint(questions_bp)
