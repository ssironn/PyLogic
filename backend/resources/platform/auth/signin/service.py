"""Servico de autenticacao de estudante."""
from datetime import datetime, timezone

from sqlalchemy import select
from werkzeug.security import check_password_hash

from app.extensions import db
from models import Student
from utils.response import Result
from utils.jwt import create_access_token, create_refresh_token


class SigninService:
    """Servico para autenticacao de estudante."""

    @staticmethod
    def signin(data: dict) -> Result[dict]:
        """
        Realiza login de estudante.

        Args:
            data: Dicionario com email e password

        Returns:
            Result contendo dados do estudante e tokens ou erro
        """
        email = data.get('email')
        password = data.get('password')

        # Query using db.session.execute with select
        stmt = select(Student).where(Student.email == email)
        result = db.session.execute(stmt)
        student = result.scalar_one_or_none()

        if not student:
            return Result.fail(
                message="Credenciais invalidas",
                code="INVALID_CREDENTIALS"
            )

        if not check_password_hash(student.password_hash, password):
            return Result.fail(
                message="Credenciais invalidas",
                code="INVALID_CREDENTIALS"
            )

        if not student.active:
            return Result.fail(
                message="Conta inativa",
                code="ACCOUNT_INACTIVE"
            )

        # Update last access
        student.last_access = datetime.now(timezone.utc)
        db.session.commit()

        # Generate tokens
        student_id = str(student.id)
        access_token = create_access_token(
            subject=student_id,
            additional_claims={
                'email': student.email,
                'name': student.name
            }
        )
        refresh_token = create_refresh_token(subject=student_id)

        return Result.success(
            value={
                'student': {
                    'id': student_id,
                    'name': student.name,
                    'email': student.email,
                    'registration_number': student.registration_number
                },
                'tokens': {
                    'access_token': access_token,
                    'refresh_token': refresh_token,
                    'token_type': 'Bearer'
                }
            },
            message="Login realizado com sucesso"
        )
