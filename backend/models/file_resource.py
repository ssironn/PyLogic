from datetime import datetime, timezone
import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column
from .base import get_uuid_type
from .content_node import ContentNode
from .enums import ContentType

class FileResource(ContentNode):
    __tablename__ = 'file_resource'

    id: Mapped[str] = mapped_column(get_uuid_type(), sa.ForeignKey('content_node.id'), primary_key=True)
    drive_file_id: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    drive_url: Mapped[str] = mapped_column(sa.String(500), nullable=False)
    original_name: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    mime_type: Mapped[str] = mapped_column(sa.String(100), nullable=False)
    size: Mapped[int] = mapped_column(sa.BigInteger, nullable=False)
    version: Mapped[int] = mapped_column(sa.Integer, default=1)
    upload_date: Mapped[datetime] = mapped_column(sa.DateTime, default=lambda: datetime.now(timezone.utc))
    file_hash: Mapped[str] = mapped_column(sa.String(64), nullable=True)

    __mapper_args__ = {
        'polymorphic_identity': ContentType.FILE,
    }

    def __repr__(self):
        return f'<FileResource {self.original_name}>'
