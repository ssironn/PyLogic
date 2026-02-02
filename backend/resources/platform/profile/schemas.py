"""Schemas para perfil do estudante."""
from apiflask import Schema
from apiflask.fields import String, DateTime, Email
from apiflask.validators import Length


class ProfileDataSchema(Schema):
    """Schema para dados do perfil."""
    id = String(metadata={'description': 'ID do estudante'})
    name = String(metadata={'description': 'Nome do estudante'})
    email = Email(metadata={'description': 'Email do estudante'})
    registration_number = String(metadata={'description': 'Numero de matricula'})
    created_at = DateTime(metadata={'description': 'Data de criacao'})
    last_access = DateTime(metadata={'description': 'Ultimo acesso'})


class ProfileUpdateRequestSchema(Schema):
    """Schema para atualizacao do perfil."""
    name = String(
        required=True,
        validate=Length(min=2, max=100),
        metadata={'description': 'Nome do estudante'}
    )
    email = Email(
        required=True,
        metadata={'description': 'Email do estudante'}
    )


class PasswordChangeRequestSchema(Schema):
    """Schema para alteracao de senha."""
    current_password = String(
        required=True,
        metadata={'description': 'Senha atual'}
    )
    new_password = String(
        required=True,
        validate=Length(min=6),
        metadata={'description': 'Nova senha (minimo 6 caracteres)'}
    )
    confirm_password = String(
        required=True,
        metadata={'description': 'Confirmacao da nova senha'}
    )
