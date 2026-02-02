from datetime import datetime, timezone
import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import BaseModel, get_uuid_type
from .enums import EnrollmentStatus

class Enrollment(BaseModel):
    __tablename__ = 'enrollment'

    student_id: Mapped[str] = mapped_column(get_uuid_type(), sa.ForeignKey('student.id'), nullable=False)
    class_group_id: Mapped[str] = mapped_column(get_uuid_type(), sa.ForeignKey('class_group.id'), nullable=False)
    enrollment_date: Mapped[datetime] = mapped_column(sa.DateTime, default=lambda: datetime.now(timezone.utc))
    status: Mapped[EnrollmentStatus] = mapped_column(sa.Enum(EnrollmentStatus), default=EnrollmentStatus.PENDING)
    extra_permissions: Mapped[dict] = mapped_column(sa.JSON, default={})

    # Relationships
    student = relationship('Student', backref='enrollments')
    class_group = relationship('ClassGroup', backref='enrollments')

    def __repr__(self):
        return f'<Enrollment {self.student_id} - {self.class_group_id}>'
