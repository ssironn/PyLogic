from datetime import datetime
import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import BaseModel, get_uuid_type
from .enums import ProgressStatus

class StudentProgress(BaseModel):
    __tablename__ = 'student_progress'

    student_id: Mapped[str] = mapped_column(get_uuid_type(), sa.ForeignKey('student.id'), nullable=False)
    content_node_id: Mapped[str] = mapped_column(get_uuid_type(), sa.ForeignKey('content_node.id'), nullable=False)
    status: Mapped[ProgressStatus] = mapped_column(sa.Enum(ProgressStatus), default=ProgressStatus.NOT_STARTED)
    percent_completed: Mapped[float] = mapped_column(sa.Float, default=0.0)
    last_access: Mapped[datetime] = mapped_column(sa.DateTime, nullable=True)
    total_time: Mapped[int] = mapped_column(sa.Integer, default=0)
    progress_data: Mapped[dict] = mapped_column(sa.JSON, default={})

    # Relationships
    student = relationship('Student', backref='progress')
    content_node = relationship('ContentNode', backref='student_progress')

    def __repr__(self):
        return f'<StudentProgress {self.student_id} - {self.content_node_id}>'
