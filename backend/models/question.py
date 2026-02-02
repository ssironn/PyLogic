"""Model for mathematical questions."""
import re
from datetime import datetime, timezone
from typing import Optional

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import BaseModel, get_uuid_type
from models.enums import QuestionDifficulty


class Question(BaseModel):
    """Represents a mathematical question."""

    __tablename__ = 'question'

    math_area_id: Mapped[str] = mapped_column(
        get_uuid_type(),
        sa.ForeignKey('math_area.id'),
        nullable=False
    )
    math_subarea_id: Mapped[Optional[str]] = mapped_column(
        get_uuid_type(),
        sa.ForeignKey('math_subarea.id'),
        nullable=True
    )
    title: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    content: Mapped[str] = mapped_column(sa.Text, nullable=False)
    content_latex: Mapped[str] = mapped_column(sa.Text, nullable=True)
    answer: Mapped[str] = mapped_column(sa.Text, nullable=True)
    answer_latex: Mapped[str] = mapped_column(sa.Text, nullable=True)
    explanation: Mapped[str] = mapped_column(sa.Text, nullable=True)
    explanation_latex: Mapped[str] = mapped_column(sa.Text, nullable=True)
    difficulty: Mapped[QuestionDifficulty] = mapped_column(
        sa.Enum(QuestionDifficulty),
        default=QuestionDifficulty.MEDIUM
    )
    tags: Mapped[list] = mapped_column(sa.JSON, default=[])
    active: Mapped[bool] = mapped_column(sa.Boolean, default=True)
    created_by: Mapped[str] = mapped_column(
        get_uuid_type(),
        sa.ForeignKey('admin.id'),
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime,
        default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        sa.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    math_area = relationship('MathArea', backref='questions')
    math_subarea = relationship('MathSubarea', backref='questions')
    creator = relationship('Admin', backref='created_questions')

    def __repr__(self) -> str:
        return f'<Question {self.title}>'

    @staticmethod
    def text_to_latex(text: str) -> str:
        """
        Convert plain text mathematical expressions to LaTeX syntax.

        This is a basic converter that handles common mathematical patterns.
        """
        if not text:
            return text

        result = text

        # Wrap mathematical expressions in $...$ if not already
        # Pattern: detect expressions with operators or numbers/variables
        math_pattern = r'(?<!\$)(\b\d+\s*[\+\-\*\/\^]\s*\d+\b|\b[a-z]\s*[\+\-\*\/\^=]\s*[a-z0-9]+\b)'

        # Replace common mathematical notations
        replacements = [
            # Fractions: a/b -> \frac{a}{b}
            (r'(\d+|\([^)]+\))\s*/\s*(\d+|\([^)]+\))', r'\\frac{\1}{\2}'),
            # Exponents: x^2 -> x^{2}, x^10 -> x^{10}
            (r'([a-zA-Z0-9])\^(\d+)', r'\1^{\2}'),
            # Square root: sqrt(x) -> \sqrt{x}
            (r'sqrt\(([^)]+)\)', r'\\sqrt{\1}'),
            # Greek letters
            (r'\balpha\b', r'\\alpha'),
            (r'\bbeta\b', r'\\beta'),
            (r'\bgamma\b', r'\\gamma'),
            (r'\bdelta\b', r'\\delta'),
            (r'\btheta\b', r'\\theta'),
            (r'\bpi\b', r'\\pi'),
            (r'\bsigma\b', r'\\sigma'),
            (r'\bomega\b', r'\\omega'),
            # Comparison operators
            (r'<=', r'\\leq'),
            (r'>=', r'\\geq'),
            (r'!=', r'\\neq'),
            # Infinity
            (r'\binfinity\b', r'\\infty'),
            (r'\binf\b', r'\\infty'),
            # Sum and product
            (r'\bsum\b', r'\\sum'),
            (r'\bprod\b', r'\\prod'),
            # Integral
            (r'\bint\b', r'\\int'),
            # Limit
            (r'\blim\b', r'\\lim'),
            # Trigonometric functions
            (r'\bsin\b', r'\\sin'),
            (r'\bcos\b', r'\\cos'),
            (r'\btan\b', r'\\tan'),
            (r'\blog\b', r'\\log'),
            (r'\bln\b', r'\\ln'),
            # Multiplication dot
            (r'\s*\*\s*', r' \\cdot '),
            # Plus/minus
            (r'\+/-', r'\\pm'),
            # Arrows
            (r'->', r'\\rightarrow'),
            (r'<-', r'\\leftarrow'),
            (r'<=>', r'\\Leftrightarrow'),
        ]

        for pattern, replacement in replacements:
            result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)

        return result

    def ensure_latex(self) -> None:
        """Ensure LaTeX versions of content, answer, and explanation exist."""
        if self.content and not self.content_latex:
            self.content_latex = self.text_to_latex(self.content)
        if self.answer and not self.answer_latex:
            self.answer_latex = self.text_to_latex(self.answer)
        if self.explanation and not self.explanation_latex:
            self.explanation_latex = self.text_to_latex(self.explanation)
