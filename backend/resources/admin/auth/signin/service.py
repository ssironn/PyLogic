"""Servico de autenticacao de administrador."""
from sqlalchemy import select
from werkzeug.security import check_password_hash

from app.extensions import db
from models import Admin
from utils.response import Result
from utils.jwt import create_access_token, create_refresh_token


class AdminSigninService:
    """Servico para autenticacao de administrador."""

    @staticmethod
    def signin(data: dict) -> Result[dict]:
        """
        Realiza login de administrador.

        Args:
            data: Dicionario com email e password

        Returns:
            Result contendo dados do admin e tokens ou erro
        """
        email = data.get('email')
        password = data.get('password')

        stmt = select(Admin).where(Admin.email == email)
        result = db.session.execute(stmt)
        admin = result.scalar_one_or_none()

        if not admin or not check_password_hash(admin.password_hash, password):
            return Result.fail(
                message="Credenciais invalidas",
                code="INVALID_CREDENTIALS"
            )

        if not admin.active:
            return Result.fail(
                message="Conta inativa",
                code="ACCOUNT_INACTIVE"
            )

        # Generate tokens
        admin_id = str(admin.id)
        access_token = create_access_token(
            subject=admin_id,
            additional_claims={
                'email': admin.email,
                'name': admin.name,
                'role': 'admin'
            }
        )
        refresh_token = create_refresh_token(subject=admin_id)

        return Result.success(
            value={
                'admin': {
                    'id': admin_id,
                    'name': admin.name,
                    'email': admin.email
                },
                'tokens': {
                    'access_token': access_token,
                    'refresh_token': refresh_token,
                    'token_type': 'Bearer'
                }
            },
            message="Login realizado com sucesso"
        )
