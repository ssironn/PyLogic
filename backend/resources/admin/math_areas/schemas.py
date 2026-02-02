"""Schemas for math areas admin endpoints."""
from apiflask import Schema
from apiflask.fields import String, Boolean, Integer
from apiflask.validators import Length


class MathAreaCreateSchema(Schema):
    """Schema for creating a math area."""
    name = String(required=True, validate=Length(min=1, max=100))
    description = String(load_default=None)
    icon = String(load_default=None, validate=Length(max=50))
    color = String(load_default=None, validate=Length(max=20))
    order = Integer(load_default=0)


class MathAreaUpdateSchema(Schema):
    """Schema for updating a math area."""
    name = String(load_default=None, validate=Length(min=1, max=100))
    description = String(load_default=None)
    icon = String(load_default=None, validate=Length(max=50))
    color = String(load_default=None, validate=Length(max=20))
    order = Integer(load_default=None)
    active = Boolean(load_default=None)


class MathSubareaCreateSchema(Schema):
    """Schema for creating a math subarea."""
    name = String(required=True, validate=Length(min=1, max=100))
    description = String(load_default=None)
    order = Integer(load_default=0)


class MathSubareaUpdateSchema(Schema):
    """Schema for updating a math subarea."""
    name = String(load_default=None, validate=Length(min=1, max=100))
    description = String(load_default=None)
    order = Integer(load_default=None)
    active = Boolean(load_default=None)
