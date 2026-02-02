from datetime import datetime, timezone
import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import BaseModel, get_uuid_type
from .enums import ContentType, ContentVisibility

class ContentNode(BaseModel):
    __tablename__ = 'content_node'

    type: Mapped[ContentType] = mapped_column(sa.Enum(ContentType), nullable=False)
    title: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    description: Mapped[str] = mapped_column(sa.Text, nullable=True)
    class_group_id: Mapped[str] = mapped_column(get_uuid_type(), sa.ForeignKey('class_group.id'), nullable=False)
    parent_id: Mapped[str] = mapped_column(get_uuid_type(), sa.ForeignKey('content_node.id'), nullable=True)
    order: Mapped[int] = mapped_column(sa.Integer, default=0)
    visibility: Mapped[ContentVisibility] = mapped_column(sa.Enum(ContentVisibility), default=ContentVisibility.PRIVATE)
    created_by: Mapped[str] = mapped_column(get_uuid_type(), sa.ForeignKey('admin.id'), nullable=False)
    created_at: Mapped[datetime] = mapped_column(sa.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(sa.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    meta_data: Mapped[dict] = mapped_column(sa.JSON, default={})

    # Polymorphic config
    __mapper_args__ = {
        'polymorphic_on': type,
        'polymorphic_identity': 'content_node'
    }

    # Relationships
    class_group = relationship('ClassGroup', backref='content_nodes')
    creator = relationship('Admin', backref='created_contents')
    children = relationship('ContentNode', backref=sa.orm.backref('parent', remote_side='ContentNode.id'))

    def __repr__(self):
        return f'<ContentNode {self.title}>'
