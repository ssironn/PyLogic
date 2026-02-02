"""Schemas para CRUD de alunos."""
from apiflask import Schema
from apiflask.fields import String, Boolean, Email, UUID
from apiflask.validators import Length


class StudentCreateSchema(Schema):
    """Schema para criacao de aluno."""
    name = String(
        required=True,
        validate=Length(min=2, max=100),
        metadata={'description': 'Nome do aluno'}
    )
    email = Email(
        required=True,
        metadata={'description': 'Email do aluno'}
    )
    password = String(
        required=True,
        validate=Length(min=6),
        metadata={'description': 'Senha do aluno'}
    )
    registration_number = String(
        required=False,
        metadata={'description': 'Numero de matricula'}
    )
    class_group_id = String(
        required=True,
        metadata={'description': 'ID da turma'}
    )


class StudentUpdateSchema(Schema):
    """Schema para atualizacao de aluno."""
    name = String(
        required=False,
        validate=Length(min=2, max=100),
        metadata={'description': 'Nome do aluno'}
    )
    email = Email(
        required=False,
        metadata={'description': 'Email do aluno'}
    )
    password = String(
        required=False,
        validate=Length(min=6),
        metadata={'description': 'Nova senha do aluno'}
    )
    registration_number = String(
        required=False,
        metadata={'description': 'Numero de matricula'}
    )
    class_group_id = String(
        required=False,
        metadata={'description': 'ID da turma'}
    )
    active = Boolean(
        required=False,
        metadata={'description': 'Status ativo do aluno'}
    )


class StudentQuerySchema(Schema):
    """Schema para filtros de listagem."""
    class_group_id = String(
        required=False,
        metadata={'description': 'Filtrar por turma'}
    )
    active = Boolean(
        required=False,
        metadata={'description': 'Filtrar por status ativo'}
    )
    search = String(
        required=False,
        metadata={'description': 'Buscar por nome ou email'}
    )
