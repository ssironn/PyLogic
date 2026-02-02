from datetime import datetime, timezone
import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import BaseModel, get_uuid_type
from .enums import AccessType

class ContentPermission(BaseModel):
    __tablename__ = 'content_permission'

    content_node_id: Mapped[str] = mapped_column(get_uuid_type(), sa.ForeignKey('content_node.id'), nullable=False)
    student_id: Mapped[str] = mapped_column(get_uuid_type(), sa.ForeignKey('student.id'), nullable=True)
    class_group_id: Mapped[str] = mapped_column(get_uuid_type(), sa.ForeignKey('class_group.id'), nullable=True)
    access_type: Mapped[AccessType] = mapped_column(sa.Enum(AccessType), nullable=False)
    granted_by: Mapped[str] = mapped_column(get_uuid_type(), sa.ForeignKey('admin.id'), nullable=False)
    granted_at: Mapped[datetime] = mapped_column(sa.DateTime, default=lambda: datetime.now(timezone.utc))
    expires_at: Mapped[datetime] = mapped_column(sa.DateTime, nullable=True)
    conditions: Mapped[dict] = mapped_column(sa.JSON, default={})

    # Relationships
    content_node = relationship('ContentNode', backref='permissions')
    student = relationship('Student', backref='permissions')
    class_group = relationship('ClassGroup', backref='permissions')
    granter = relationship('Admin', backref='granted_permissions')

    def __repr__(self):
        return f'<ContentPermission {self.id}>'
