"""Model for mathematical subareas."""
from datetime import datetime, timezone

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import BaseModel, get_uuid_type


class MathSubarea(BaseModel):
    """Represents a mathematical subarea within an area."""

    __tablename__ = 'math_subarea'

    math_area_id: Mapped[str] = mapped_column(
        get_uuid_type(),
        sa.ForeignKey('math_area.id'),
        nullable=False
    )
    name: Mapped[str] = mapped_column(sa.String(100), nullable=False)
    description: Mapped[str] = mapped_column(sa.Text, nullable=True)
    order: Mapped[int] = mapped_column(sa.Integer, default=0)
    active: Mapped[bool] = mapped_column(sa.Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime,
        default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        sa.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    # Relationship to parent area
    math_area = relationship('MathArea', back_populates='subareas')

    # Unique constraint: name must be unique within each area
    __table_args__ = (
        sa.UniqueConstraint('math_area_id', 'name', name='uq_math_subarea_area_name'),
    )

    def __repr__(self) -> str:
        return f'<MathSubarea {self.name}>'
