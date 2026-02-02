"""Servico para atualizar perfil do estudante."""
from sqlalchemy import select

from app.extensions import db
from models import Student
from utils.response import Result


class ProfileUpdateService:
    """Servico para atualizar perfil do estudante."""

    @staticmethod
    def update_profile(student_id: str, data: dict) -> Result[dict]:
        """
        Atualiza o perfil do estudante.

        Args:
            student_id: ID do estudante
            data: Dados para atualizacao (name, email)

        Returns:
            Result contendo dados atualizados ou erro
        """
        stmt = select(Student).where(Student.id == student_id)
        result = db.session.execute(stmt)
        student = result.scalar_one_or_none()

        if not student:
            return Result.fail(
                message="Estudante nao encontrado",
                code="NOT_FOUND"
            )

        new_email = data.get('email')

        # Check if email is already in use by another student
        if new_email and new_email != student.email:
            email_check = select(Student).where(
                Student.email == new_email,
                Student.id != student_id
            )
            existing = db.session.execute(email_check).scalar_one_or_none()

            if existing:
                return Result.fail(
                    message="Este email ja esta em uso",
                    code="EMAIL_IN_USE",
                    field="email"
                )

        # Update fields
        if data.get('name'):
            student.name = data['name']
        if new_email:
            student.email = new_email

        db.session.commit()

        return Result.success(
            value={
                'id': str(student.id),
                'name': student.name,
                'email': student.email,
                'registration_number': student.registration_number
            },
            message="Perfil atualizado com sucesso"
        )
