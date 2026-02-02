"""
Authentication utilities for admin routes.

Provides decorators for admin-only route protection.
"""
from functools import wraps
from typing import Optional

from flask import request, g
from werkzeug.exceptions import Unauthorized, Forbidden

from utils.jwt import verify_token


def get_token_from_header() -> Optional[str]:
    """Extract JWT token from Authorization header."""
    auth_header = request.headers.get('Authorization', '')

    if not auth_header.startswith('Bearer '):
        return None

    return auth_header[7:]  # Remove 'Bearer ' prefix


def require_admin(f):
    """
    Decorator that requires a valid admin JWT token.

    Extracts the token from the Authorization header, validates it,
    verifies the user has admin role, and stores admin info in Flask's g object.

    Usage:
        @app.route('/admin-only')
        @require_admin
        def admin_route():
            admin_id = get_current_admin_id()
            ...
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = get_token_from_header()

        if not token:
            raise Unauthorized("Token de autenticacao nao fornecido")

        payload = verify_token(token, token_type='access')

        if not payload:
            raise Unauthorized("Token invalido ou expirado")

        # Check if user has admin role
        if payload.get('role') != 'admin':
            raise Forbidden("Acesso restrito a administradores")

        # Store admin info in Flask's g object
        g.current_admin_id = payload.get('sub')
        g.current_admin_email = payload.get('email')
        g.current_admin_name = payload.get('name')

        return f(*args, **kwargs)

    return decorated


def get_current_admin_id() -> Optional[str]:
    """Get the current authenticated admin's ID."""
    return getattr(g, 'current_admin_id', None)


def get_current_admin_email() -> Optional[str]:
    """Get the current authenticated admin's email."""
    return getattr(g, 'current_admin_email', None)


def get_current_admin_name() -> Optional[str]:
    """Get the current authenticated admin's name."""
    return getattr(g, 'current_admin_name', None)
