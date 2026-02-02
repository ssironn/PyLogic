from datetime import datetime, timezone
import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import BaseModel, get_uuid_type

class ClassConfig(BaseModel):
    __tablename__ = 'class_config'

    class_group_id: Mapped[str] = mapped_column(get_uuid_type(), sa.ForeignKey('class_group.id'), nullable=False)
    config_type: Mapped[str] = mapped_column(sa.String(50), nullable=False)
    value: Mapped[dict] = mapped_column(sa.JSON, default={})
    updated_by: Mapped[str] = mapped_column(get_uuid_type(), sa.ForeignKey('admin.id'), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(sa.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    class_group = relationship('ClassGroup', backref='configs_list')
    updater = relationship('Admin', backref='updated_configs')

    def __repr__(self):
        return f'<ClassConfig {self.config_type}>'
