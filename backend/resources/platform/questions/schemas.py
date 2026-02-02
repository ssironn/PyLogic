"""Schemas for platform questions endpoints."""
from apiflask import Schema
from apiflask.fields import String
from apiflask.validators import OneOf, Length


class QuestionQuerySchema(Schema):
    """Schema for filtering questions."""
    math_area_id = String(load_default=None)
    math_subarea_id = String(load_default=None)
    difficulty = String(load_default=None, validate=OneOf(['facil', 'medio', 'dificil', 'especialista']))
    search = String(load_default=None)


class AnswerSubmitSchema(Schema):
    """Schema for submitting an answer."""
    content = String(required=True, validate=Length(min=1))
    content_latex = String(load_default=None)
