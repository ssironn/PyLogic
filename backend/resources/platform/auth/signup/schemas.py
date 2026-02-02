"""Schemas para cadastro de estudante."""
from apiflask import Schema
from apiflask.fields import Email, String
from apiflask.validators import Length


class SignupRequestSchema(Schema):
    """Schema para requisicao de cadastro."""
    name = String(
        required=True,
        validate=Length(min=2, max=100),
        metadata={'description': 'Nome do estudante'}
    )
    email = Email(
        required=True,
        metadata={'description': 'Email do estudante'}
    )
    password = String(
        required=True,
        validate=Length(min=6),
        metadata={'description': 'Senha (minimo 6 caracteres)'}
    )
    confirm_password = String(
        required=True,
        metadata={'description': 'Confirmacao da senha'}
    )
    registration_number = String(
        required=False,
        metadata={'description': 'Numero de matricula (opcional)'}
    )
    access_code = String(
        required=True,
        metadata={'description': 'Codigo de acesso da turma'}
    )
