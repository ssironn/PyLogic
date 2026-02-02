"""Servico para alteracao de senha do estudante."""
from sqlalchemy import select
from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db
from models import Student
from utils.response import Result


class PasswordChangeService:
    """Servico para alteracao de senha."""

    @staticmethod
    def change_password(student_id: str, data: dict) -> Result[None]:
        """
        Altera a senha do estudante.

        Args:
            student_id: ID do estudante
            data: Dados com current_password, new_password, confirm_password

        Returns:
            Result indicando sucesso ou erro
        """
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        confirm_password = data.get('confirm_password')

        # Validate passwords match
        if new_password != confirm_password:
            return Result.fail(
                message="As senhas nao conferem",
                code="PASSWORD_MISMATCH",
                field="confirm_password"
            )

        # Get student
        stmt = select(Student).where(Student.id == student_id)
        result = db.session.execute(stmt)
        student = result.scalar_one_or_none()

        if not student:
            return Result.fail(
                message="Estudante nao encontrado",
                code="NOT_FOUND"
            )

        # Verify current password
        if not check_password_hash(student.password_hash, current_password):
            return Result.fail(
                message="Senha atual incorreta",
                code="INVALID_PASSWORD",
                field="current_password"
            )

        # Update password
        student.password_hash = generate_password_hash(new_password)
        db.session.commit()

        return Result.success(
            value=None,
            message="Senha alterada com sucesso"
        )
