"""Servico de CRUD de turmas."""
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.orm import joinedload

from app.extensions import db
from models import ClassGroup
from utils.response import Result


class ClassGroupService:
    """Servico para gerenciamento de turmas."""

    @staticmethod
    def list(admin_id: str, active: Optional[bool] = None, search: Optional[str] = None) -> Result[list]:
        """
        Lista todas as turmas do administrador.

        Args:
            admin_id: ID do administrador
            active: Filtrar por status ativo
            search: Buscar por nome

        Returns:
            Result contendo lista de turmas
        """
        stmt = select(ClassGroup).where(ClassGroup.admin_id == admin_id)

        if active is not None:
            stmt = stmt.where(ClassGroup.active == active)

        if search:
            stmt = stmt.where(ClassGroup.name.ilike(f'%{search}%'))

        stmt = stmt.order_by(ClassGroup.created_at.desc())

        result = db.session.execute(stmt)
        class_groups = result.scalars().all()

        return Result.success(
            value=[
                {
                    'id': str(cg.id),
                    'name': cg.name,
                    'description': cg.description,
                    'access_code': cg.access_code,
                    'active': cg.active,
                    'configs': cg.configs,
                    'created_at': cg.created_at.isoformat() if cg.created_at else None,
                    'student_count': len(cg.students) if cg.students else 0
                }
                for cg in class_groups
            ]
        )

    @staticmethod
    def get(class_group_id: str, admin_id: str) -> Result[dict]:
        """
        Obtem uma turma pelo ID.

        Args:
            class_group_id: ID da turma
            admin_id: ID do administrador

        Returns:
            Result contendo dados da turma
        """
        stmt = select(ClassGroup).where(
            ClassGroup.id == class_group_id,
            ClassGroup.admin_id == admin_id
        )
        result = db.session.execute(stmt)
        class_group = result.scalar_one_or_none()

        if not class_group:
            return Result.fail(
                message="Turma nao encontrada",
                code="NOT_FOUND"
            )

        return Result.success(
            value={
                'id': str(class_group.id),
                'name': class_group.name,
                'description': class_group.description,
                'access_code': class_group.access_code,
                'active': class_group.active,
                'configs': class_group.configs,
                'created_at': class_group.created_at.isoformat() if class_group.created_at else None,
                'student_count': len(class_group.students) if class_group.students else 0
            }
        )

    @staticmethod
    def create(data: dict, admin_id: str) -> Result[dict]:
        """
        Cria uma nova turma.

        Args:
            data: Dados da turma
            admin_id: ID do administrador

        Returns:
            Result contendo dados da turma criada
        """
        # Check if access_code already exists
        stmt = select(ClassGroup).where(ClassGroup.access_code == data.get('access_code'))
        result = db.session.execute(stmt)
        existing = result.scalar_one_or_none()

        if existing:
            return Result.fail(
                message="Codigo de acesso ja existe",
                code="ACCESS_CODE_EXISTS",
                field="access_code"
            )

        class_group = ClassGroup(
            name=data.get('name'),
            description=data.get('description', ''),
            access_code=data.get('access_code'),
            admin_id=admin_id,
            configs=data.get('configs', {}),
            active=True,
            created_at=datetime.now(timezone.utc)
        )

        db.session.add(class_group)
        db.session.commit()

        return Result.success(
            value={
                'id': str(class_group.id),
                'name': class_group.name,
                'description': class_group.description,
                'access_code': class_group.access_code,
                'active': class_group.active,
                'configs': class_group.configs,
                'created_at': class_group.created_at.isoformat() if class_group.created_at else None
            },
            message="Turma criada com sucesso"
        )

    @staticmethod
    def update(class_group_id: str, data: dict, admin_id: str) -> Result[dict]:
        """
        Atualiza uma turma.

        Args:
            class_group_id: ID da turma
            data: Dados para atualizar
            admin_id: ID do administrador

        Returns:
            Result contendo dados atualizados
        """
        stmt = select(ClassGroup).where(
            ClassGroup.id == class_group_id,
            ClassGroup.admin_id == admin_id
        )
        result = db.session.execute(stmt)
        class_group = result.scalar_one_or_none()

        if not class_group:
            return Result.fail(
                message="Turma nao encontrada",
                code="NOT_FOUND"
            )

        # Check if new access_code already exists
        if 'access_code' in data and data['access_code'] != class_group.access_code:
            stmt = select(ClassGroup).where(ClassGroup.access_code == data['access_code'])
            result = db.session.execute(stmt)
            existing = result.scalar_one_or_none()

            if existing:
                return Result.fail(
                    message="Codigo de acesso ja existe",
                    code="ACCESS_CODE_EXISTS",
                    field="access_code"
                )

        # Update fields
        if 'name' in data:
            class_group.name = data['name']
        if 'description' in data:
            class_group.description = data['description']
        if 'access_code' in data:
            class_group.access_code = data['access_code']
        if 'active' in data:
            class_group.active = data['active']
        if 'configs' in data:
            class_group.configs = data['configs']

        db.session.commit()

        return Result.success(
            value={
                'id': str(class_group.id),
                'name': class_group.name,
                'description': class_group.description,
                'access_code': class_group.access_code,
                'active': class_group.active,
                'configs': class_group.configs,
                'created_at': class_group.created_at.isoformat() if class_group.created_at else None
            },
            message="Turma atualizada com sucesso"
        )

    @staticmethod
    def delete(class_group_id: str, admin_id: str) -> Result[None]:
        """
        Remove uma turma.

        Args:
            class_group_id: ID da turma
            admin_id: ID do administrador

        Returns:
            Result indicando sucesso ou erro
        """
        stmt = select(ClassGroup).where(
            ClassGroup.id == class_group_id,
            ClassGroup.admin_id == admin_id
        )
        result = db.session.execute(stmt)
        class_group = result.scalar_one_or_none()

        if not class_group:
            return Result.fail(
                message="Turma nao encontrada",
                code="NOT_FOUND"
            )

        # Check if class has students
        if class_group.students and len(class_group.students) > 0:
            return Result.fail(
                message="Nao e possivel excluir turma com alunos matriculados",
                code="HAS_STUDENTS"
            )

        db.session.delete(class_group)
        db.session.commit()

        return Result.success(
            value=None,
            message="Turma removida com sucesso"
        )
