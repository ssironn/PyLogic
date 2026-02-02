from datetime import datetime, timezone
import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import BaseModel, get_uuid_type

class DriveConfig(BaseModel):
    __tablename__ = 'drive_config'

    class_group_id: Mapped[str] = mapped_column(get_uuid_type(), sa.ForeignKey('class_group.id'), nullable=False)
    drive_folder_id: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    service_account: Mapped[dict] = mapped_column(sa.JSON, nullable=False)
    auto_sync: Mapped[bool] = mapped_column(sa.Boolean, default=False)
    last_sync: Mapped[datetime] = mapped_column(sa.DateTime, nullable=True)

    # Relationships
    class_group = relationship('ClassGroup', backref='drive_config', uselist=False)

    def __repr__(self):
        return f'<DriveConfig {self.drive_folder_id}>'
