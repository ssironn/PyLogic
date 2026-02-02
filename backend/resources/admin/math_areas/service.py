"""Service for math areas CRUD operations."""
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select, func

from app.extensions import db
from models import MathArea, MathSubarea, Question
from utils.response import Result


class MathAreaService:
    """Service for managing math areas."""

    @staticmethod
    def _serialize_area(area: MathArea) -> dict:
        """Serialize a math area to dictionary."""
        # Count subareas
        stmt = select(func.count(MathSubarea.id)).where(
            MathSubarea.math_area_id == area.id,
            MathSubarea.active == True
        )
        subarea_count = db.session.execute(stmt).scalar() or 0

        # Count questions
        stmt = select(func.count(Question.id)).where(
            Question.math_area_id == area.id
        )
        question_count = db.session.execute(stmt).scalar() or 0

        return {
            'id': str(area.id),
            'name': area.name,
            'description': area.description,
            'icon': area.icon,
            'color': area.color,
            'order': area.order,
            'active': area.active,
            'subarea_count': subarea_count,
            'question_count': question_count,
            'created_at': area.created_at.isoformat() if area.created_at else None,
            'updated_at': area.updated_at.isoformat() if area.updated_at else None,
        }

    @staticmethod
    def _serialize_subarea(subarea: MathSubarea) -> dict:
        """Serialize a math subarea to dictionary."""
        # Count questions
        stmt = select(func.count(Question.id)).where(
            Question.math_subarea_id == subarea.id
        )
        question_count = db.session.execute(stmt).scalar() or 0

        return {
            'id': str(subarea.id),
            'math_area_id': str(subarea.math_area_id),
            'math_area_name': subarea.math_area.name if subarea.math_area else None,
            'name': subarea.name,
            'description': subarea.description,
            'order': subarea.order,
            'active': subarea.active,
            'question_count': question_count,
            'created_at': subarea.created_at.isoformat() if subarea.created_at else None,
            'updated_at': subarea.updated_at.isoformat() if subarea.updated_at else None,
        }

    @staticmethod
    def list_areas(include_inactive: bool = False) -> Result[list]:
        """List all math areas."""
        stmt = select(MathArea)
        if not include_inactive:
            stmt = stmt.where(MathArea.active == True)
        stmt = stmt.order_by(MathArea.order, MathArea.name)

        result = db.session.execute(stmt)
        areas = result.scalars().all()

        return Result.success(
            value=[MathAreaService._serialize_area(a) for a in areas]
        )

    @staticmethod
    def get_area(area_id: str) -> Result[dict]:
        """Get a math area by ID."""
        stmt = select(MathArea).where(MathArea.id == area_id)
        result = db.session.execute(stmt)
        area = result.scalar_one_or_none()

        if not area:
            return Result.fail(
                message="Area matematica nao encontrada",
                code="NOT_FOUND"
            )

        return Result.success(value=MathAreaService._serialize_area(area))

    @staticmethod
    def create_area(data: dict) -> Result[dict]:
        """Create a new math area."""
        # Check for duplicate name
        stmt = select(MathArea).where(MathArea.name == data.get('name'))
        result = db.session.execute(stmt)
        existing = result.scalar_one_or_none()

        if existing:
            return Result.fail(
                message="Ja existe uma area com esse nome",
                code="DUPLICATE_NAME",
                field="name"
            )

        area = MathArea(
            name=data.get('name'),
            description=data.get('description'),
            icon=data.get('icon'),
            color=data.get('color'),
            order=data.get('order', 0),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

        db.session.add(area)
        db.session.commit()

        return Result.success(
            value=MathAreaService._serialize_area(area),
            message="Area criada com sucesso"
        )

    @staticmethod
    def update_area(area_id: str, data: dict) -> Result[dict]:
        """Update a math area."""
        stmt = select(MathArea).where(MathArea.id == area_id)
        result = db.session.execute(stmt)
        area = result.scalar_one_or_none()

        if not area:
            return Result.fail(
                message="Area matematica nao encontrada",
                code="NOT_FOUND"
            )

        # Check for duplicate name if name is being updated
        if data.get('name') and data.get('name') != area.name:
            stmt = select(MathArea).where(
                MathArea.name == data.get('name'),
                MathArea.id != area_id
            )
            result = db.session.execute(stmt)
            existing = result.scalar_one_or_none()

            if existing:
                return Result.fail(
                    message="Ja existe uma area com esse nome",
                    code="DUPLICATE_NAME",
                    field="name"
                )

        # Update fields
        if data.get('name'):
            area.name = data['name']
        if 'description' in data:
            area.description = data['description']
        if 'icon' in data:
            area.icon = data['icon']
        if 'color' in data:
            area.color = data['color']
        if data.get('order') is not None:
            area.order = data['order']
        if data.get('active') is not None:
            area.active = data['active']

        area.updated_at = datetime.now(timezone.utc)

        db.session.commit()

        return Result.success(
            value=MathAreaService._serialize_area(area),
            message="Area atualizada com sucesso"
        )

    @staticmethod
    def delete_area(area_id: str) -> Result[None]:
        """Delete a math area."""
        stmt = select(MathArea).where(MathArea.id == area_id)
        result = db.session.execute(stmt)
        area = result.scalar_one_or_none()

        if not area:
            return Result.fail(
                message="Area matematica nao encontrada",
                code="NOT_FOUND"
            )

        # Check if there are questions using this area
        stmt = select(func.count(Question.id)).where(Question.math_area_id == area_id)
        question_count = db.session.execute(stmt).scalar() or 0

        if question_count > 0:
            return Result.fail(
                message=f"Nao e possivel excluir. Existem {question_count} questoes vinculadas a esta area.",
                code="HAS_QUESTIONS"
            )

        # Delete subareas first
        stmt = select(MathSubarea).where(MathSubarea.math_area_id == area_id)
        result = db.session.execute(stmt)
        subareas = result.scalars().all()
        for subarea in subareas:
            db.session.delete(subarea)

        db.session.delete(area)
        db.session.commit()

        return Result.success(
            value=None,
            message="Area removida com sucesso"
        )

    # Subarea methods

    @staticmethod
    def list_subareas(area_id: str, include_inactive: bool = False) -> Result[list]:
        """List subareas of a math area."""
        # Verify area exists
        stmt = select(MathArea).where(MathArea.id == area_id)
        result = db.session.execute(stmt)
        area = result.scalar_one_or_none()

        if not area:
            return Result.fail(
                message="Area matematica nao encontrada",
                code="NOT_FOUND"
            )

        stmt = select(MathSubarea).where(MathSubarea.math_area_id == area_id)
        if not include_inactive:
            stmt = stmt.where(MathSubarea.active == True)
        stmt = stmt.order_by(MathSubarea.order, MathSubarea.name)

        result = db.session.execute(stmt)
        subareas = result.scalars().all()

        return Result.success(
            value=[MathAreaService._serialize_subarea(s) for s in subareas]
        )

    @staticmethod
    def get_subarea(subarea_id: str) -> Result[dict]:
        """Get a subarea by ID."""
        stmt = select(MathSubarea).where(MathSubarea.id == subarea_id)
        result = db.session.execute(stmt)
        subarea = result.scalar_one_or_none()

        if not subarea:
            return Result.fail(
                message="Subarea nao encontrada",
                code="NOT_FOUND"
            )

        return Result.success(value=MathAreaService._serialize_subarea(subarea))

    @staticmethod
    def create_subarea(area_id: str, data: dict) -> Result[dict]:
        """Create a new subarea."""
        # Verify area exists
        stmt = select(MathArea).where(MathArea.id == area_id)
        result = db.session.execute(stmt)
        area = result.scalar_one_or_none()

        if not area:
            return Result.fail(
                message="Area matematica nao encontrada",
                code="AREA_NOT_FOUND",
                field="math_area_id"
            )

        # Check for duplicate name within the same area
        stmt = select(MathSubarea).where(
            MathSubarea.math_area_id == area_id,
            MathSubarea.name == data.get('name')
        )
        result = db.session.execute(stmt)
        existing = result.scalar_one_or_none()

        if existing:
            return Result.fail(
                message="Ja existe uma subarea com esse nome nesta area",
                code="DUPLICATE_NAME",
                field="name"
            )

        subarea = MathSubarea(
            math_area_id=area_id,
            name=data.get('name'),
            description=data.get('description'),
            order=data.get('order', 0),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

        db.session.add(subarea)
        db.session.commit()

        return Result.success(
            value=MathAreaService._serialize_subarea(subarea),
            message="Subarea criada com sucesso"
        )

    @staticmethod
    def update_subarea(subarea_id: str, data: dict) -> Result[dict]:
        """Update a subarea."""
        stmt = select(MathSubarea).where(MathSubarea.id == subarea_id)
        result = db.session.execute(stmt)
        subarea = result.scalar_one_or_none()

        if not subarea:
            return Result.fail(
                message="Subarea nao encontrada",
                code="NOT_FOUND"
            )

        # Check for duplicate name if name is being updated
        if data.get('name') and data.get('name') != subarea.name:
            stmt = select(MathSubarea).where(
                MathSubarea.math_area_id == subarea.math_area_id,
                MathSubarea.name == data.get('name'),
                MathSubarea.id != subarea_id
            )
            result = db.session.execute(stmt)
            existing = result.scalar_one_or_none()

            if existing:
                return Result.fail(
                    message="Ja existe uma subarea com esse nome nesta area",
                    code="DUPLICATE_NAME",
                    field="name"
                )

        # Update fields
        if data.get('name'):
            subarea.name = data['name']
        if 'description' in data:
            subarea.description = data['description']
        if data.get('order') is not None:
            subarea.order = data['order']
        if data.get('active') is not None:
            subarea.active = data['active']

        subarea.updated_at = datetime.now(timezone.utc)

        db.session.commit()

        return Result.success(
            value=MathAreaService._serialize_subarea(subarea),
            message="Subarea atualizada com sucesso"
        )

    @staticmethod
    def delete_subarea(subarea_id: str) -> Result[None]:
        """Delete a subarea."""
        stmt = select(MathSubarea).where(MathSubarea.id == subarea_id)
        result = db.session.execute(stmt)
        subarea = result.scalar_one_or_none()

        if not subarea:
            return Result.fail(
                message="Subarea nao encontrada",
                code="NOT_FOUND"
            )

        # Check if there are questions using this subarea
        stmt = select(func.count(Question.id)).where(Question.math_subarea_id == subarea_id)
        question_count = db.session.execute(stmt).scalar() or 0

        if question_count > 0:
            return Result.fail(
                message=f"Nao e possivel excluir. Existem {question_count} questoes vinculadas a esta subarea.",
                code="HAS_QUESTIONS"
            )

        db.session.delete(subarea)
        db.session.commit()

        return Result.success(
            value=None,
            message="Subarea removida com sucesso"
        )
