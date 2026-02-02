"""Servico para obter perfil do estudante."""
from sqlalchemy import select

from app.extensions import db
from models import Student
from utils.response import Result


class ProfileGetService:
    """Servico para obter perfil do estudante."""

    @staticmethod
    def get_profile(student_id: str) -> Result[dict]:
        """
        Obtem o perfil do estudante.

        Args:
            student_id: ID do estudante

        Returns:
            Result contendo dados do perfil ou erro
        """
        stmt = select(Student).where(Student.id == student_id)
        result = db.session.execute(stmt)
        student = result.scalar_one_or_none()

        if not student:
            return Result.fail(
                message="Estudante nao encontrado",
                code="NOT_FOUND"
            )

        return Result.success({
            'id': str(student.id),
            'name': student.name,
            'email': student.email,
            'registration_number': student.registration_number,
            'created_at': student.created_at.isoformat() if student.created_at else None,
            'last_access': student.last_access.isoformat() if student.last_access else None
        })
