from datetime import datetime, timezone
import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import BaseModel, get_uuid_type

class Student(BaseModel):
    __tablename__ = 'student'

    name: Mapped[str] = mapped_column(sa.String(100), nullable=False)
    email: Mapped[str] = mapped_column(sa.String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    registration_number: Mapped[str] = mapped_column(sa.String(50), unique=True, nullable=True)
    created_at: Mapped[datetime] = mapped_column(sa.DateTime, default=lambda: datetime.now(timezone.utc))
    last_access: Mapped[datetime] = mapped_column(sa.DateTime, nullable=True)
    active: Mapped[bool] = mapped_column(sa.Boolean, default=True)
    class_group_id: Mapped[str] = mapped_column(get_uuid_type(), sa.ForeignKey('class_group.id'), nullable=False)

    # Relationships
    class_group = relationship('ClassGroup', backref='students')

    def __repr__(self):
        return f'<Student {self.email}>'
