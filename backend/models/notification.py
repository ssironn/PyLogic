from datetime import datetime, timezone
import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import BaseModel, get_uuid_type
from .enums import NotificationType

class Notification(BaseModel):
    __tablename__ = 'notification'

    student_id: Mapped[str] = mapped_column(get_uuid_type(), sa.ForeignKey('student.id'), nullable=False)
    title: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    message: Mapped[str] = mapped_column(sa.Text, nullable=False)
    type: Mapped[NotificationType] = mapped_column(sa.Enum(NotificationType), default=NotificationType.INFO)
    read: Mapped[bool] = mapped_column(sa.Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(sa.DateTime, default=lambda: datetime.now(timezone.utc))
    destination_link: Mapped[str] = mapped_column(sa.String(500), nullable=True)
    context: Mapped[dict] = mapped_column(sa.JSON, default={})

    # Relationships
    student = relationship('Student', backref='notifications')

    def __repr__(self):
        return f'<Notification {self.title}>'
