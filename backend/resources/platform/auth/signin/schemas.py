"""Schemas para autenticacao de estudante."""
from apiflask import Schema
from apiflask.fields import Email, String, Nested


class SigninRequestSchema(Schema):
    """Schema para requisicao de login."""
    email = Email(
        required=True,
        metadata={'description': 'Email do estudante'}
    )
    password = String(
        required=True,
        metadata={'description': 'Senha do estudante'}
    )


class TokenResponseSchema(Schema):
    """Schema para resposta com tokens."""
    access_token = String(metadata={'description': 'Token de acesso JWT'})
    refresh_token = String(metadata={'description': 'Token de refresh JWT'})
    token_type = String(metadata={'description': 'Tipo do token (Bearer)'})


class StudentDataSchema(Schema):
    """Schema para dados do estudante."""
    id = String(metadata={'description': 'ID do estudante'})
    name = String(metadata={'description': 'Nome do estudante'})
    email = String(metadata={'description': 'Email do estudante'})
    registration_number = String(metadata={'description': 'Numero de matricula'})
