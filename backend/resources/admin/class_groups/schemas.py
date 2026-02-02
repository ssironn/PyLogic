"""Schemas para CRUD de turmas."""
from apiflask import Schema
from apiflask.fields import String, Boolean, Dict, UUID
from apiflask.validators import Length


class ClassGroupCreateSchema(Schema):
    """Schema para criacao de turma."""
    name = String(
        required=True,
        validate=Length(min=2, max=100),
        metadata={'description': 'Nome da turma'}
    )
    description = String(
        required=False,
        metadata={'description': 'Descricao da turma'}
    )
    access_code = String(
        required=True,
        validate=Length(min=4, max=20),
        metadata={'description': 'Codigo de acesso para alunos'}
    )
    configs = Dict(
        required=False,
        metadata={'description': 'Configuracoes extras da turma'}
    )


class ClassGroupUpdateSchema(Schema):
    """Schema para atualizacao de turma."""
    name = String(
        required=False,
        validate=Length(min=2, max=100),
        metadata={'description': 'Nome da turma'}
    )
    description = String(
        required=False,
        metadata={'description': 'Descricao da turma'}
    )
    access_code = String(
        required=False,
        validate=Length(min=4, max=20),
        metadata={'description': 'Codigo de acesso para alunos'}
    )
    active = Boolean(
        required=False,
        metadata={'description': 'Status ativo da turma'}
    )
    configs = Dict(
        required=False,
        metadata={'description': 'Configuracoes extras da turma'}
    )


class ClassGroupQuerySchema(Schema):
    """Schema para filtros de listagem."""
    active = Boolean(
        required=False,
        metadata={'description': 'Filtrar por status ativo'}
    )
    search = String(
        required=False,
        metadata={'description': 'Buscar por nome'}
    )
