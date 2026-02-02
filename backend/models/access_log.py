from datetime import datetime, timezone
import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import BaseModel, get_uuid_type
from .enums import ActionType

class AccessLog(BaseModel):
    __tablename__ = 'access_log'

    student_id: Mapped[str] = mapped_column(get_uuid_type(), sa.ForeignKey('student.id'), nullable=False)
    content_node_id: Mapped[str] = mapped_column(get_uuid_type(), sa.ForeignKey('content_node.id'), nullable=False)
    action_type: Mapped[ActionType] = mapped_column(sa.Enum(ActionType), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(sa.DateTime, default=lambda: datetime.now(timezone.utc))
    ip_address: Mapped[str] = mapped_column(sa.String(45), nullable=True)
    user_agent: Mapped[str] = mapped_column(sa.String(500), nullable=True)
    details: Mapped[dict] = mapped_column(sa.JSON, default={})

    # Relationships
    student = relationship('Student', backref='access_logs')
    content_node = relationship('ContentNode', backref='access_logs')

    def __repr__(self):
        return f'<AccessLog {self.id}>'
