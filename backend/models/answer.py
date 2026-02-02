"""Answer model for student submissions."""
import re
from typing import Optional

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import BaseModel, get_uuid_type
from models.enums import AnswerStatus


class Answer(BaseModel):
    """Model for student answers to questions."""

    __tablename__ = 'answer'

    student_id: Mapped[str] = mapped_column(
        get_uuid_type(),
        sa.ForeignKey('student.id', ondelete='CASCADE'),
        nullable=False
    )
    question_id: Mapped[str] = mapped_column(
        get_uuid_type(),
        sa.ForeignKey('question.id', ondelete='CASCADE'),
        nullable=False
    )
    content: Mapped[str] = mapped_column(sa.Text, nullable=False)
    content_latex: Mapped[Optional[str]] = mapped_column(sa.Text, nullable=True)

    # Admin review fields
    status: Mapped[AnswerStatus] = mapped_column(
        sa.Enum(AnswerStatus),
        default=AnswerStatus.PENDING,
        nullable=False
    )
    is_correct: Mapped[Optional[bool]] = mapped_column(sa.Boolean, nullable=True)
    feedback: Mapped[Optional[str]] = mapped_column(sa.Text, nullable=True)
    score: Mapped[Optional[float]] = mapped_column(sa.Float, nullable=True)
    reviewed_by: Mapped[Optional[str]] = mapped_column(get_uuid_type(), nullable=True)
    reviewed_at: Mapped[Optional[sa.DateTime]] = mapped_column(sa.DateTime, nullable=True)

    # Relationships
    student = relationship('Student', backref='answers')
    question = relationship('Question', backref='answers')

    # Unique constraint: one answer per student per question (can be updated)
    __table_args__ = (
        sa.UniqueConstraint('student_id', 'question_id', name='uq_answer_student_question'),
    )

    @staticmethod
    def text_to_latex(text: str) -> str:
        """Convert plain text with mathematical expressions to LaTeX format."""
        if not text:
            return text

        result = text

        # Fractions: a/b -> \frac{a}{b}
        result = re.sub(
            r'(\d+|\([^)]+\))\s*/\s*(\d+|\([^)]+\))',
            r'\\frac{\1}{\2}',
            result
        )

        # Exponents: x^2, x^n, x^{expr}
        result = re.sub(r'\^(\d+)', r'^{\1}', result)
        result = re.sub(r'\^([a-zA-Z])', r'^{\1}', result)

        # Subscripts: x_1, x_n
        result = re.sub(r'_(\d+)', r'_{\1}', result)
        result = re.sub(r'_([a-zA-Z])', r'_{\1}', result)

        # Square roots: sqrt(x) -> \sqrt{x}
        result = re.sub(r'sqrt\(([^)]+)\)', r'\\sqrt{\1}', result)

        # Greek letters
        greek_letters = [
            'alpha', 'beta', 'gamma', 'delta', 'epsilon', 'theta',
            'lambda', 'mu', 'pi', 'sigma', 'phi', 'omega',
            'Alpha', 'Beta', 'Gamma', 'Delta', 'Theta', 'Lambda',
            'Pi', 'Sigma', 'Phi', 'Omega',
        ]
        for name in greek_letters:
            result = re.sub(rf'\b{name}\b', f'\\{name}', result)

        # Common functions
        functions = ['sin', 'cos', 'tan', 'log', 'ln', 'exp', 'lim', 'sum', 'int']
        for func in functions:
            result = re.sub(rf'\b{func}\b', f'\\{func}', result)

        # Infinity
        result = re.sub(r'\binfinity\b|\binf\b', r'\\infty', result, flags=re.IGNORECASE)

        # Plus/minus
        result = re.sub(r'\+/-', r'\\pm', result)

        # Not equal
        result = re.sub(r'!=|<>', r'\\neq', result)

        # Less/greater or equal
        result = re.sub(r'<=', r'\\leq', result)
        result = re.sub(r'>=', r'\\geq', result)

        # Arrows
        result = re.sub(r'->', r'\\rightarrow', result)
        result = re.sub(r'<-', r'\\leftarrow', result)
        result = re.sub(r'=>', r'\\Rightarrow', result)

        return result

    def ensure_latex(self):
        """Ensure LaTeX version exists for content."""
        if self.content and not self.content_latex:
            self.content_latex = self.text_to_latex(self.content)
