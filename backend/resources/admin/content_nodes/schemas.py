"""Schemas para CRUD de conteudos."""
from apiflask import Schema
from apiflask.fields import String, Integer, Boolean, Dict, Date
from apiflask.validators import Length, OneOf
from marshmallow import validates_schema, ValidationError


class ContentNodeBaseSchema(Schema):
    """Schema base para conteudo."""
    title = String(
        required=True,
        validate=Length(min=1, max=200),
        metadata={'description': 'Titulo do conteudo'}
    )
    description = String(
        required=False,
        metadata={'description': 'Descricao do conteudo'}
    )
    class_group_id = String(
        required=True,
        metadata={'description': 'ID da turma'}
    )
    parent_id = String(
        required=False,
        metadata={'description': 'ID do conteudo pai (pasta)'}
    )
    order = Integer(
        required=False,
        metadata={'description': 'Ordem de exibicao'}
    )
    visibility = String(
        required=False,
        validate=OneOf(['publico', 'privado', 'restrito']),
        metadata={'description': 'Visibilidade do conteudo'}
    )
    meta_data = Dict(
        required=False,
        metadata={'description': 'Metadados extras'}
    )


class FolderCreateSchema(ContentNodeBaseSchema):
    """Schema para criacao de pasta."""
    type = String(
        load_default='pasta',
        metadata={'description': 'Tipo de conteudo'}
    )
    color = String(
        required=False,
        metadata={'description': 'Cor da pasta'}
    )
    icon = String(
        required=False,
        metadata={'description': 'Icone da pasta'}
    )
    allow_upload = Boolean(
        required=False,
        load_default=False,
        metadata={'description': 'Permitir upload de alunos'}
    )


class FileResourceCreateSchema(ContentNodeBaseSchema):
    """Schema para criacao de arquivo."""
    type = String(
        load_default='arquivo',
        metadata={'description': 'Tipo de conteudo'}
    )
    drive_file_id = String(
        required=True,
        metadata={'description': 'ID do arquivo no Drive'}
    )
    drive_url = String(
        required=True,
        metadata={'description': 'URL do arquivo no Drive'}
    )
    original_name = String(
        required=True,
        metadata={'description': 'Nome original do arquivo'}
    )
    mime_type = String(
        required=True,
        metadata={'description': 'Tipo MIME do arquivo'}
    )
    size = Integer(
        required=True,
        metadata={'description': 'Tamanho do arquivo em bytes'}
    )
    file_hash = String(
        required=False,
        metadata={'description': 'Hash do arquivo'}
    )


class YouTubeLinkCreateSchema(ContentNodeBaseSchema):
    """Schema para criacao de link do YouTube."""
    type = String(
        load_default='youtube',
        metadata={'description': 'Tipo de conteudo'}
    )
    youtube_id = String(
        required=True,
        metadata={'description': 'ID do video no YouTube'}
    )
    full_url = String(
        required=True,
        metadata={'description': 'URL completa do video'}
    )
    duration = Integer(
        required=False,
        metadata={'description': 'Duracao em segundos'}
    )
    thumbnail_url = String(
        required=False,
        metadata={'description': 'URL da thumbnail'}
    )
    channel = String(
        required=False,
        metadata={'description': 'Nome do canal'}
    )
    published_at = Date(
        required=False,
        metadata={'description': 'Data de publicacao'}
    )


class ContentNodeCreateSchema(Schema):
    """Schema unificado para criacao de conteudo."""
    type = String(
        required=True,
        validate=OneOf(['pasta', 'arquivo', 'youtube']),
        metadata={'description': 'Tipo de conteudo: pasta, arquivo, youtube'}
    )
    title = String(
        required=True,
        validate=Length(min=1, max=200),
        metadata={'description': 'Titulo do conteudo'}
    )
    description = String(
        required=False,
        metadata={'description': 'Descricao do conteudo'}
    )
    class_group_id = String(
        required=True,
        metadata={'description': 'ID da turma'}
    )
    parent_id = String(
        required=False,
        metadata={'description': 'ID do conteudo pai (pasta)'}
    )
    order = Integer(
        required=False,
        metadata={'description': 'Ordem de exibicao'}
    )
    visibility = String(
        required=False,
        validate=OneOf(['publico', 'privado', 'restrito']),
        metadata={'description': 'Visibilidade do conteudo'}
    )
    meta_data = Dict(
        required=False,
        metadata={'description': 'Metadados extras'}
    )
    # Folder specific
    color = String(required=False)
    icon = String(required=False)
    allow_upload = Boolean(required=False, load_default=False)
    # FileResource specific
    drive_file_id = String(required=False)
    drive_url = String(required=False)
    original_name = String(required=False)
    mime_type = String(required=False)
    size = Integer(required=False)
    file_hash = String(required=False)
    # YouTubeLink specific
    youtube_id = String(required=False)
    full_url = String(required=False)
    duration = Integer(required=False)
    thumbnail_url = String(required=False)
    channel = String(required=False)
    published_at = Date(required=False)


class ContentNodeUpdateSchema(Schema):
    """Schema para atualizacao de conteudo."""
    title = String(
        required=False,
        validate=Length(min=1, max=200),
        metadata={'description': 'Titulo do conteudo'}
    )
    description = String(
        required=False,
        metadata={'description': 'Descricao do conteudo'}
    )
    parent_id = String(
        required=False,
        metadata={'description': 'ID do conteudo pai (pasta)'}
    )
    order = Integer(
        required=False,
        metadata={'description': 'Ordem de exibicao'}
    )
    visibility = String(
        required=False,
        validate=OneOf(['publico', 'privado', 'restrito']),
        metadata={'description': 'Visibilidade do conteudo'}
    )
    meta_data = Dict(
        required=False,
        metadata={'description': 'Metadados extras'}
    )
    # Folder specific
    color = String(required=False)
    icon = String(required=False)
    allow_upload = Boolean(required=False)
    # YouTubeLink specific
    duration = Integer(required=False)
    thumbnail_url = String(required=False)
    channel = String(required=False)


class ContentNodeQuerySchema(Schema):
    """Schema para filtros de listagem."""
    class_group_id = String(
        required=False,
        metadata={'description': 'Filtrar por turma'}
    )
    parent_id = String(
        required=False,
        metadata={'description': 'Filtrar por pasta pai (use "null" para raiz)'}
    )
    type = String(
        required=False,
        validate=OneOf(['pasta', 'arquivo', 'youtube']),
        metadata={'description': 'Filtrar por tipo'}
    )
    visibility = String(
        required=False,
        validate=OneOf(['publico', 'privado', 'restrito']),
        metadata={'description': 'Filtrar por visibilidade'}
    )
    search = String(
        required=False,
        metadata={'description': 'Buscar por titulo'}
    )
