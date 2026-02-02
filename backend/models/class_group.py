from datetime import datetime, timezone
import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import BaseModel, get_uuid_type

class ClassGroup(BaseModel):
    __tablename__ = 'class_group'

    name: Mapped[str] = mapped_column(sa.String(100), nullable=False)
    description: Mapped[str] = mapped_column(sa.Text)
    access_code: Mapped[str] = mapped_column(sa.String(20), unique=True, nullable=False)
    admin_id: Mapped[str] = mapped_column(get_uuid_type(), sa.ForeignKey('admin.id'), nullable=False)
    created_at: Mapped[datetime] = mapped_column(sa.DateTime, default=lambda: datetime.now(timezone.utc))
    active: Mapped[bool] = mapped_column(sa.Boolean, default=True)
    configs: Mapped[dict] = mapped_column(sa.JSON, default={})

    # Relationships
    admin = relationship('Admin', backref='class_groups')

    def __repr__(self):
        return f'<ClassGroup {self.name}>'
