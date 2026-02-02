"""Model for mathematical areas."""
from datetime import datetime, timezone

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import BaseModel, get_uuid_type


class MathArea(BaseModel):
    """Represents a mathematical area (e.g., Algebra, Geometry)."""

    __tablename__ = 'math_area'

    name: Mapped[str] = mapped_column(sa.String(100), nullable=False, unique=True)
    description: Mapped[str] = mapped_column(sa.Text, nullable=True)
    icon: Mapped[str] = mapped_column(sa.String(50), nullable=True)
    color: Mapped[str] = mapped_column(sa.String(20), nullable=True)
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

    # Relationship to subareas
    subareas = relationship('MathSubarea', back_populates='math_area', lazy='dynamic')

    def __repr__(self) -> str:
        return f'<MathArea {self.name}>'
