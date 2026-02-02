from apiflask import Schema
from apiflask.fields import Email, String


class AdminSigninSchema(Schema):
    """Schema para login de administrador."""
    email = Email(required=True)
    password = String(required=True)
