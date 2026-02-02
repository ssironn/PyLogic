"""Schemas for questions admin endpoints."""
from apiflask import Schema
from apiflask.fields import String, Boolean, List, Nested
from apiflask.validators import OneOf, Length


class QuestionCreateSchema(Schema):
    """Schema for creating a question."""
    math_area_id = String(required=True)
    math_subarea_id = String(load_default=None)
    title = String(required=True, validate=Length(min=1, max=255))
    content = String(required=True)
    content_latex = String(load_default=None)
    answer = String(load_default=None)
    answer_latex = String(load_default=None)
    explanation = String(load_default=None)
    explanation_latex = String(load_default=None)
    difficulty = String(
        load_default='medio',
        validate=OneOf(['facil', 'medio', 'dificil', 'especialista'])
    )
    tags = List(String(), load_default=[])


class QuestionUpdateSchema(Schema):
    """Schema for updating a question."""
    math_area_id = String(load_default=None)
    math_subarea_id = String(load_default=None)
    title = String(load_default=None, validate=Length(min=1, max=255))
    content = String(load_default=None)
    content_latex = String(load_default=None)
    answer = String(load_default=None)
    answer_latex = String(load_default=None)
    explanation = String(load_default=None)
    explanation_latex = String(load_default=None)
    difficulty = String(
        load_default=None,
        validate=OneOf(['facil', 'medio', 'dificil', 'especialista'])
    )
    tags = List(String(), load_default=None)
    active = Boolean(load_default=None)


class QuestionQuerySchema(Schema):
    """Schema for filtering questions."""
    math_area_id = String(load_default=None)
    math_subarea_id = String(load_default=None)
    difficulty = String(load_default=None)
    active = Boolean(load_default=None)
    search = String(load_default=None)
