"""
JWT token utilities.

Provides functions for creating and validating JWT tokens.
"""
from datetime import datetime, timezone, timedelta
from typing import Optional, Any
import jwt

from app.config import get_config


def create_access_token(
    subject: str,
    additional_claims: Optional[dict[str, Any]] = None,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a new access token.

    Args:
        subject: The subject of the token (usually user ID)
        additional_claims: Additional claims to include in the token
        expires_delta: Custom expiration time

    Returns:
        Encoded JWT token string
    """
    config = get_config()

    now = datetime.now(timezone.utc)
    expires = expires_delta or config.JWT_ACCESS_TOKEN_EXPIRES

    payload = {
        'sub': subject,
        'iat': now,
        'exp': now + expires,
        'type': 'access'
    }

    if additional_claims:
        payload.update(additional_claims)

    return jwt.encode(
        payload,
        config.JWT_SECRET_KEY,
        algorithm=config.JWT_ALGORITHM
    )


def create_refresh_token(
    subject: str,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a new refresh token.

    Args:
        subject: The subject of the token (usually user ID)
        expires_delta: Custom expiration time

    Returns:
        Encoded JWT refresh token string
    """
    config = get_config()

    now = datetime.now(timezone.utc)
    expires = expires_delta or config.JWT_REFRESH_TOKEN_EXPIRES

    payload = {
        'sub': subject,
        'iat': now,
        'exp': now + expires,
        'type': 'refresh'
    }

    return jwt.encode(
        payload,
        config.JWT_SECRET_KEY,
        algorithm=config.JWT_ALGORITHM
    )


def decode_token(token: str) -> dict[str, Any]:
    """
    Decode and validate a JWT token.

    Args:
        token: The JWT token string

    Returns:
        Decoded token payload

    Raises:
        jwt.ExpiredSignatureError: If token has expired
        jwt.InvalidTokenError: If token is invalid
    """
    config = get_config()

    return jwt.decode(
        token,
        config.JWT_SECRET_KEY,
        algorithms=[config.JWT_ALGORITHM]
    )


def verify_token(token: str, token_type: str = 'access') -> Optional[dict[str, Any]]:
    """
    Verify a JWT token and return payload if valid.

    Args:
        token: The JWT token string
        token_type: Expected token type ('access' or 'refresh')

    Returns:
        Token payload if valid, None otherwise
    """
    try:
        payload = decode_token(token)

        if payload.get('type') != token_type:
            return None

        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def get_token_subject(token: str) -> Optional[str]:
    """
    Extract the subject (user ID) from a token.

    Args:
        token: The JWT token string

    Returns:
        The subject string if token is valid, None otherwise
    """
    payload = verify_token(token)
    return payload.get('sub') if payload else None
