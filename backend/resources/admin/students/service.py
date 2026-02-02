"""Servico de CRUD de alunos."""
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select, or_
from sqlalchemy.orm import joinedload
from werkzeug.security import generate_password_hash

from app.extensions import db
from models import Student, ClassGroup, Enrollment
from models.enums import EnrollmentStatus
from utils.response import Result


class StudentService:
    """Servico para gerenciamento de alunos."""

    @staticmethod
    def list(
        admin_id: str,
        class_group_id: Optional[str] = None,
        active: Optional[bool] = None,
        search: Optional[str] = None
    ) -> Result[list]:
        """
        Lista alunos das turmas do administrador.

        Args:
            admin_id: ID do administrador
            class_group_id: Filtrar por turma
            active: Filtrar por status ativo
            search: Buscar por nome ou email

        Returns:
            Result contendo lista de alunos
        """
        # Get admin's class groups
        class_groups_stmt = select(ClassGroup.id).where(ClassGroup.admin_id == admin_id)

        stmt = (
            select(Student)
            .options(joinedload(Student.class_group))
            .where(Student.class_group_id.in_(class_groups_stmt))
        )

        if class_group_id:
            stmt = stmt.where(Student.class_group_id == class_group_id)

        if active is not None:
            stmt = stmt.where(Student.active == active)

        if search:
            stmt = stmt.where(
                or_(
                    Student.name.ilike(f'%{search}%'),
                    Student.email.ilike(f'%{search}%')
                )
            )

        stmt = stmt.order_by(Student.created_at.desc())

        result = db.session.execute(stmt)
        students = result.scalars().unique().all()

        return Result.success(
            value=[
                {
                    'id': str(s.id),
                    'name': s.name,
                    'email': s.email,
                    'registration_number': s.registration_number,
                    'active': s.active,
                    'class_group_id': str(s.class_group_id),
                    'class_group_name': s.class_group.name if s.class_group else None,
                    'created_at': s.created_at.isoformat() if s.created_at else None,
                    'last_access': s.last_access.isoformat() if s.last_access else None
                }
                for s in students
            ]
        )

    @staticmethod
    def get(student_id: str, admin_id: str) -> Result[dict]:
        """
        Obtem um aluno pelo ID.

        Args:
            student_id: ID do aluno
            admin_id: ID do administrador

        Returns:
            Result contendo dados do aluno
        """
        # Get admin's class groups
        class_groups_stmt = select(ClassGroup.id).where(ClassGroup.admin_id == admin_id)

        stmt = (
            select(Student)
            .options(joinedload(Student.class_group))
            .where(
                Student.id == student_id,
                Student.class_group_id.in_(class_groups_stmt)
            )
        )
        result = db.session.execute(stmt)
        student = result.scalar_one_or_none()

        if not student:
            return Result.fail(
                message="Aluno nao encontrado",
                code="NOT_FOUND"
            )

        return Result.success(
            value={
                'id': str(student.id),
                'name': student.name,
                'email': student.email,
                'registration_number': student.registration_number,
                'active': student.active,
                'class_group_id': str(student.class_group_id),
                'class_group_name': student.class_group.name if student.class_group else None,
                'created_at': student.created_at.isoformat() if student.created_at else None,
                'last_access': student.last_access.isoformat() if student.last_access else None
            }
        )

    @staticmethod
    def create(data: dict, admin_id: str) -> Result[dict]:
        """
        Cria um novo aluno.

        Args:
            data: Dados do aluno
            admin_id: ID do administrador

        Returns:
            Result contendo dados do aluno criado
        """
        # Verify class group belongs to admin
        stmt = select(ClassGroup).where(
            ClassGroup.id == data.get('class_group_id'),
            ClassGroup.admin_id == admin_id
        )
        result = db.session.execute(stmt)
        class_group = result.scalar_one_or_none()

        if not class_group:
            return Result.fail(
                message="Turma nao encontrada",
                code="CLASS_GROUP_NOT_FOUND",
                field="class_group_id"
            )

        # Check if email already exists
        stmt = select(Student).where(Student.email == data.get('email'))
        result = db.session.execute(stmt)
        existing = result.scalar_one_or_none()

        if existing:
            return Result.fail(
                message="Email ja cadastrado",
                code="EMAIL_EXISTS",
                field="email"
            )

        # Check if registration_number already exists
        if data.get('registration_number'):
            stmt = select(Student).where(
                Student.registration_number == data.get('registration_number')
            )
            result = db.session.execute(stmt)
            existing = result.scalar_one_or_none()

            if existing:
                return Result.fail(
                    message="Numero de matricula ja cadastrado",
                    code="REGISTRATION_EXISTS",
                    field="registration_number"
                )

        student = Student(
            name=data.get('name'),
            email=data.get('email'),
            password_hash=generate_password_hash(data.get('password')),
            registration_number=data.get('registration_number'),
            class_group_id=data.get('class_group_id'),
            active=True,
            created_at=datetime.now(timezone.utc)
        )

        db.session.add(student)
        db.session.flush()

        # Create enrollment
        enrollment = Enrollment(
            student_id=student.id,
            class_group_id=class_group.id,
            enrollment_date=datetime.now(timezone.utc),
            status=EnrollmentStatus.ACTIVE
        )

        db.session.add(enrollment)
        db.session.commit()

        return Result.success(
            value={
                'id': str(student.id),
                'name': student.name,
                'email': student.email,
                'registration_number': student.registration_number,
                'active': student.active,
                'class_group_id': str(student.class_group_id),
                'class_group_name': class_group.name,
                'created_at': student.created_at.isoformat() if student.created_at else None
            },
            message="Aluno criado com sucesso"
        )

    @staticmethod
    def update(student_id: str, data: dict, admin_id: str) -> Result[dict]:
        """
        Atualiza um aluno.

        Args:
            student_id: ID do aluno
            data: Dados para atualizar
            admin_id: ID do administrador

        Returns:
            Result contendo dados atualizados
        """
        # Get admin's class groups
        class_groups_stmt = select(ClassGroup.id).where(ClassGroup.admin_id == admin_id)

        stmt = (
            select(Student)
            .options(joinedload(Student.class_group))
            .where(
                Student.id == student_id,
                Student.class_group_id.in_(class_groups_stmt)
            )
        )
        result = db.session.execute(stmt)
        student = result.scalar_one_or_none()

        if not student:
            return Result.fail(
                message="Aluno nao encontrado",
                code="NOT_FOUND"
            )

        # Check if new email already exists
        if 'email' in data and data['email'] != student.email:
            stmt = select(Student).where(Student.email == data['email'])
            result = db.session.execute(stmt)
            existing = result.scalar_one_or_none()

            if existing:
                return Result.fail(
                    message="Email ja cadastrado",
                    code="EMAIL_EXISTS",
                    field="email"
                )

        # Check new class_group belongs to admin
        if 'class_group_id' in data:
            stmt = select(ClassGroup).where(
                ClassGroup.id == data['class_group_id'],
                ClassGroup.admin_id == admin_id
            )
            result = db.session.execute(stmt)
            new_class_group = result.scalar_one_or_none()

            if not new_class_group:
                return Result.fail(
                    message="Turma nao encontrada",
                    code="CLASS_GROUP_NOT_FOUND",
                    field="class_group_id"
                )

        # Update fields
        if 'name' in data:
            student.name = data['name']
        if 'email' in data:
            student.email = data['email']
        if 'password' in data:
            student.password_hash = generate_password_hash(data['password'])
        if 'registration_number' in data:
            student.registration_number = data['registration_number']
        if 'class_group_id' in data:
            student.class_group_id = data['class_group_id']
        if 'active' in data:
            student.active = data['active']

        db.session.commit()

        # Refresh to get updated class_group
        db.session.refresh(student)

        return Result.success(
            value={
                'id': str(student.id),
                'name': student.name,
                'email': student.email,
                'registration_number': student.registration_number,
                'active': student.active,
                'class_group_id': str(student.class_group_id),
                'class_group_name': student.class_group.name if student.class_group else None,
                'created_at': student.created_at.isoformat() if student.created_at else None,
                'last_access': student.last_access.isoformat() if student.last_access else None
            },
            message="Aluno atualizado com sucesso"
        )

    @staticmethod
    def delete(student_id: str, admin_id: str) -> Result[None]:
        """
        Remove um aluno.

        Args:
            student_id: ID do aluno
            admin_id: ID do administrador

        Returns:
            Result indicando sucesso ou erro
        """
        # Get admin's class groups
        class_groups_stmt = select(ClassGroup.id).where(ClassGroup.admin_id == admin_id)

        stmt = select(Student).where(
            Student.id == student_id,
            Student.class_group_id.in_(class_groups_stmt)
        )
        result = db.session.execute(stmt)
        student = result.scalar_one_or_none()

        if not student:
            return Result.fail(
                message="Aluno nao encontrado",
                code="NOT_FOUND"
            )

        # Delete enrollments first
        stmt = select(Enrollment).where(Enrollment.student_id == student_id)
        result = db.session.execute(stmt)
        enrollments = result.scalars().all()

        for enrollment in enrollments:
            db.session.delete(enrollment)

        db.session.delete(student)
        db.session.commit()

        return Result.success(
            value=None,
            message="Aluno removido com sucesso"
        )
