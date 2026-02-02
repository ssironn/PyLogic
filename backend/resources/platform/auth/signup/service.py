"""Servico de cadastro de estudante."""
from datetime import datetime, timezone

from sqlalchemy import select
from werkzeug.security import generate_password_hash

from app.extensions import db
from models import Student, ClassGroup, Enrollment
from models.enums import EnrollmentStatus
from utils.response import Result
from utils.jwt import create_access_token, create_refresh_token


class SignupService:
    """Servico para cadastro de estudante."""

    @staticmethod
    def signup(data: dict) -> Result[dict]:
        """
        Realiza cadastro de estudante.

        Args:
            data: Dicionario com dados do cadastro

        Returns:
            Result contendo dados do estudante e tokens ou erro
        """
        name = data.get('name')
        email = data.get('email')
        password = data.get('password')
        confirm_password = data.get('confirm_password')
        registration_number = data.get('registration_number')
        access_code = data.get('access_code')

        # Validate passwords match
        if password != confirm_password:
            return Result.fail(
                message="As senhas nao conferem",
                code="PASSWORD_MISMATCH",
                field="confirm_password"
            )

        # Check if email already exists
        stmt = select(Student).where(Student.email == email)
        result = db.session.execute(stmt)
        existing_student = result.scalar_one_or_none()

        if existing_student:
            return Result.fail(
                message="Este email ja esta cadastrado",
                code="EMAIL_EXISTS",
                field="email"
            )

        # Validate access code and get class group
        stmt = select(ClassGroup).where(
            ClassGroup.access_code == access_code,
            ClassGroup.active == True
        )
        result = db.session.execute(stmt)
        class_group = result.scalar_one_or_none()

        if not class_group:
            return Result.fail(
                message="Codigo de acesso invalido",
                code="INVALID_ACCESS_CODE",
                field="access_code"
            )

        # Create student
        student = Student(
            name=name,
            email=email,
            password_hash=generate_password_hash(password),
            registration_number=registration_number,
            class_group_id=class_group.id,
            active=True,
            created_at=datetime.now(timezone.utc)
        )

        db.session.add(student)
        db.session.flush()  # Get the student ID

        # Create enrollment
        enrollment = Enrollment(
            student_id=student.id,
            class_group_id=class_group.id,
            enrollment_date=datetime.now(timezone.utc),
            status=EnrollmentStatus.ACTIVE
        )

        db.session.add(enrollment)
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
            message="Cadastro realizado com sucesso"
        )
