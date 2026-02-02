import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column
from .base import get_uuid_type
from .content_node import ContentNode
from .enums import ContentType

class Folder(ContentNode):
    __tablename__ = 'folder'

    id: Mapped[str] = mapped_column(get_uuid_type(), sa.ForeignKey('content_node.id'), primary_key=True)
    color: Mapped[str] = mapped_column(sa.String(20), nullable=True)
    icon: Mapped[str] = mapped_column(sa.String(50), nullable=True)
    allow_upload: Mapped[bool] = mapped_column(sa.Boolean, default=False)

    __mapper_args__ = {
        'polymorphic_identity': ContentType.FOLDER,
    }

    def __repr__(self):
        return f'<Folder {self.title}>'
