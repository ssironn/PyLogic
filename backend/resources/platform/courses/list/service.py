"""Servico de listagem de cursos do estudante."""
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.extensions import db
from models import Enrollment, ClassGroup
from models.enums import EnrollmentStatus
from utils.response import Result


class CoursesListService:
    """Servico para listar cursos do estudante."""

    @staticmethod
    def list_courses(student_id: str) -> Result[list[dict]]:
        """
        Lista os cursos em que o estudante esta matriculado.

        Args:
            student_id: ID do estudante

        Returns:
            Result contendo lista de matriculas ou erro
        """
        stmt = (
            select(Enrollment)
            .options(joinedload(Enrollment.class_group))
            .where(Enrollment.student_id == student_id)
            .where(Enrollment.status == EnrollmentStatus.ACTIVE)
        )

        result = db.session.execute(stmt)
        enrollments = result.scalars().all()

        courses = []
        for enrollment in enrollments:
            class_group = enrollment.class_group
            courses.append({
                'id': str(enrollment.id),
                'enrollment_date': enrollment.enrollment_date.isoformat(),
                'status': enrollment.status.value,
                'class_group': {
                    'id': str(class_group.id),
                    'name': class_group.name,
                    'description': class_group.description or ''
                }
            })

        return Result.success(courses)
