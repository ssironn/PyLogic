from datetime import date
import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column
from .base import get_uuid_type
from .content_node import ContentNode
from .enums import ContentType

class YouTubeLink(ContentNode):
    __tablename__ = 'youtube_link'

    id: Mapped[str] = mapped_column(get_uuid_type(), sa.ForeignKey('content_node.id'), primary_key=True)
    youtube_id: Mapped[str] = mapped_column(sa.String(20), nullable=False)
    full_url: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    duration: Mapped[int] = mapped_column(sa.Integer, nullable=True)
    thumbnail_url: Mapped[str] = mapped_column(sa.String(500), nullable=True)
    channel: Mapped[str] = mapped_column(sa.String(100), nullable=True)
    published_at: Mapped[date] = mapped_column(sa.Date, nullable=True)

    __mapper_args__ = {
        'polymorphic_identity': ContentType.YOUTUBE,
    }

    def __repr__(self):
        return f'<YouTubeLink {self.title}>'
