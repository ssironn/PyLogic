"""Schemas for answers admin endpoints."""
from apiflask import Schema
from apiflask.fields import String, Boolean, Float
from apiflask.validators import OneOf


class AnswerReviewSchema(Schema):
    """Schema for reviewing an answer."""
    status = String(required=True, validate=OneOf(['aprovado', 'rejeitado']))
    is_correct = Boolean(load_default=None)
    feedback = String(load_default=None)
    score = Float(load_default=None)


class AnswerQuerySchema(Schema):
    """Schema for filtering answers."""
    question_id = String(load_default=None)
    student_id = String(load_default=None)
    status = String(load_default=None, validate=OneOf(['pendente', 'aprovado', 'rejeitado']))
