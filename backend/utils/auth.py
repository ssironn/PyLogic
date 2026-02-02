"""
Authentication utilities for protecting routes.

Provides decorators and helpers for JWT-based authentication.
"""
from functools import wraps
from typing import Optional

from flask import request, g
from werkzeug.exceptions import Unauthorized

from utils.jwt import verify_token


def get_token_from_header() -> Optional[str]:
    """Extract JWT token from Authorization header."""
    auth_header = request.headers.get('Authorization', '')

    if not auth_header.startswith('Bearer '):
        return None

    return auth_header[7:]  # Remove 'Bearer ' prefix


def require_auth(f):
    """
    Decorator that requires a valid JWT token.

    Extracts the token from the Authorization header, validates it,
    and stores the user ID in Flask's g object.

    Usage:
        @app.route('/protected')
        @require_auth
        def protected_route():
            user_id = get_current_user_id()
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

        # Store user info in Flask's g object
        g.current_user_id = payload.get('sub')
        g.current_user_email = payload.get('email')
        g.current_user_name = payload.get('name')

        return f(*args, **kwargs)

    return decorated


def get_current_user_id() -> Optional[str]:
    """Get the current authenticated user's ID."""
    return getattr(g, 'current_user_id', None)


def get_current_user_email() -> Optional[str]:
    """Get the current authenticated user's email."""
    return getattr(g, 'current_user_email', None)


def get_current_user_name() -> Optional[str]:
    """Get the current authenticated user's name."""
    return getattr(g, 'current_user_name', None)
