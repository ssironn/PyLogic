"""Servico de CRUD de conteudos."""
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select, or_
from sqlalchemy.orm import joinedload

from app.extensions import db
from models import ContentNode, ClassGroup, Folder, FileResource, YouTubeLink
from models.enums import ContentType, ContentVisibility
from utils.response import Result


class ContentNodeService:
    """Servico para gerenciamento de conteudos."""

    @staticmethod
    def _serialize_content_node(node: ContentNode) -> dict:
        """Serializa um conteudo para dicionario."""
        base = {
            'id': str(node.id),
            'type': node.type.value if node.type else None,
            'title': node.title,
            'description': node.description,
            'class_group_id': str(node.class_group_id),
            'parent_id': str(node.parent_id) if node.parent_id else None,
            'order': node.order,
            'visibility': node.visibility.value if node.visibility else None,
            'created_by': str(node.created_by),
            'created_at': node.created_at.isoformat() if node.created_at else None,
            'updated_at': node.updated_at.isoformat() if node.updated_at else None,
            'meta_data': node.meta_data
        }

        # Add type-specific fields
        if isinstance(node, Folder):
            base['color'] = node.color
            base['icon'] = node.icon
            base['allow_upload'] = node.allow_upload
        elif isinstance(node, FileResource):
            base['drive_file_id'] = node.drive_file_id
            base['drive_url'] = node.drive_url
            base['original_name'] = node.original_name
            base['mime_type'] = node.mime_type
            base['size'] = node.size
            base['version'] = node.version
            base['upload_date'] = node.upload_date.isoformat() if node.upload_date else None
            base['file_hash'] = node.file_hash
        elif isinstance(node, YouTubeLink):
            base['youtube_id'] = node.youtube_id
            base['full_url'] = node.full_url
            base['duration'] = node.duration
            base['thumbnail_url'] = node.thumbnail_url
            base['channel'] = node.channel
            base['published_at'] = node.published_at.isoformat() if node.published_at else None

        return base

    @staticmethod
    def list(
        admin_id: str,
        class_group_id: Optional[str] = None,
        parent_id: Optional[str] = None,
        content_type: Optional[str] = None,
        visibility: Optional[str] = None,
        search: Optional[str] = None
    ) -> Result[list]:
        """
        Lista conteudos das turmas do administrador.

        Args:
            admin_id: ID do administrador
            class_group_id: Filtrar por turma
            parent_id: Filtrar por pasta pai
            content_type: Filtrar por tipo
            visibility: Filtrar por visibilidade
            search: Buscar por titulo

        Returns:
            Result contendo lista de conteudos
        """
        # Get admin's class groups
        class_groups_stmt = select(ClassGroup.id).where(ClassGroup.admin_id == admin_id)

        stmt = select(ContentNode).where(ContentNode.class_group_id.in_(class_groups_stmt))

        if class_group_id:
            stmt = stmt.where(ContentNode.class_group_id == class_group_id)

        if parent_id:
            if parent_id == 'null':
                stmt = stmt.where(ContentNode.parent_id.is_(None))
            else:
                stmt = stmt.where(ContentNode.parent_id == parent_id)

        if content_type:
            type_map = {
                'pasta': ContentType.FOLDER,
                'arquivo': ContentType.FILE,
                'youtube': ContentType.YOUTUBE
            }
            if content_type in type_map:
                stmt = stmt.where(ContentNode.type == type_map[content_type])

        if visibility:
            visibility_map = {
                'publico': ContentVisibility.PUBLIC,
                'privado': ContentVisibility.PRIVATE,
                'restrito': ContentVisibility.RESTRICTED
            }
            if visibility in visibility_map:
                stmt = stmt.where(ContentNode.visibility == visibility_map[visibility])

        if search:
            stmt = stmt.where(ContentNode.title.ilike(f'%{search}%'))

        stmt = stmt.order_by(ContentNode.order, ContentNode.created_at.desc())

        result = db.session.execute(stmt)
        nodes = result.scalars().all()

        return Result.success(
            value=[ContentNodeService._serialize_content_node(node) for node in nodes]
        )

    @staticmethod
    def get(content_id: str, admin_id: str) -> Result[dict]:
        """
        Obtem um conteudo pelo ID.

        Args:
            content_id: ID do conteudo
            admin_id: ID do administrador

        Returns:
            Result contendo dados do conteudo
        """
        # Get admin's class groups
        class_groups_stmt = select(ClassGroup.id).where(ClassGroup.admin_id == admin_id)

        stmt = select(ContentNode).where(
            ContentNode.id == content_id,
            ContentNode.class_group_id.in_(class_groups_stmt)
        )
        result = db.session.execute(stmt)
        node = result.scalar_one_or_none()

        if not node:
            return Result.fail(
                message="Conteudo nao encontrado",
                code="NOT_FOUND"
            )

        return Result.success(
            value=ContentNodeService._serialize_content_node(node)
        )

    @staticmethod
    def create(data: dict, admin_id: str) -> Result[dict]:
        """
        Cria um novo conteudo.

        Args:
            data: Dados do conteudo
            admin_id: ID do administrador

        Returns:
            Result contendo dados do conteudo criado
        """
        # Verify class group belongs to admin
        stmt = select(ClassGroup).where(
            ClassGroup.id == data.get('class_group_id'),
            ClassGroup.admin_id == admin_id
        )
        result = db.session.execute(stmt)
        class_group = result.scalar_one_or_none()

        if not class_group:
            return Result.fail(
                message="Turma nao encontrada",
                code="CLASS_GROUP_NOT_FOUND",
                field="class_group_id"
            )

        # If parent_id is provided, verify it exists and belongs to same class
        if data.get('parent_id'):
            stmt = select(ContentNode).where(
                ContentNode.id == data.get('parent_id'),
                ContentNode.class_group_id == data.get('class_group_id'),
                ContentNode.type == ContentType.FOLDER
            )
            result = db.session.execute(stmt)
            parent = result.scalar_one_or_none()

            if not parent:
                return Result.fail(
                    message="Pasta pai nao encontrada",
                    code="PARENT_NOT_FOUND",
                    field="parent_id"
                )

        content_type = data.get('type')
        visibility_str = data.get('visibility', 'privado')
        visibility_map = {
            'publico': ContentVisibility.PUBLIC,
            'privado': ContentVisibility.PRIVATE,
            'restrito': ContentVisibility.RESTRICTED
        }
        visibility = visibility_map.get(visibility_str, ContentVisibility.PRIVATE)

        # Create based on type
        if content_type == 'pasta':
            node = Folder(
                title=data.get('title'),
                description=data.get('description'),
                class_group_id=data.get('class_group_id'),
                parent_id=data.get('parent_id'),
                order=data.get('order', 0),
                visibility=visibility,
                created_by=admin_id,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
                meta_data=data.get('meta_data', {}),
                color=data.get('color'),
                icon=data.get('icon'),
                allow_upload=data.get('allow_upload', False)
            )
        elif content_type == 'arquivo':
            if not all([data.get('drive_file_id'), data.get('drive_url'),
                       data.get('original_name'), data.get('mime_type'), data.get('size')]):
                return Result.fail(
                    message="Campos obrigatorios para arquivo nao fornecidos",
                    code="MISSING_FILE_FIELDS"
                )

            node = FileResource(
                title=data.get('title'),
                description=data.get('description'),
                class_group_id=data.get('class_group_id'),
                parent_id=data.get('parent_id'),
                order=data.get('order', 0),
                visibility=visibility,
                created_by=admin_id,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
                meta_data=data.get('meta_data', {}),
                drive_file_id=data.get('drive_file_id'),
                drive_url=data.get('drive_url'),
                original_name=data.get('original_name'),
                mime_type=data.get('mime_type'),
                size=data.get('size'),
                file_hash=data.get('file_hash'),
                upload_date=datetime.now(timezone.utc)
            )
        elif content_type == 'youtube':
            if not all([data.get('youtube_id'), data.get('full_url')]):
                return Result.fail(
                    message="Campos obrigatorios para YouTube nao fornecidos",
                    code="MISSING_YOUTUBE_FIELDS"
                )

            node = YouTubeLink(
                title=data.get('title'),
                description=data.get('description'),
                class_group_id=data.get('class_group_id'),
                parent_id=data.get('parent_id'),
                order=data.get('order', 0),
                visibility=visibility,
                created_by=admin_id,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
                meta_data=data.get('meta_data', {}),
                youtube_id=data.get('youtube_id'),
                full_url=data.get('full_url'),
                duration=data.get('duration'),
                thumbnail_url=data.get('thumbnail_url'),
                channel=data.get('channel'),
                published_at=data.get('published_at')
            )
        else:
            return Result.fail(
                message="Tipo de conteudo invalido",
                code="INVALID_TYPE",
                field="type"
            )

        db.session.add(node)
        db.session.commit()

        return Result.success(
            value=ContentNodeService._serialize_content_node(node),
            message="Conteudo criado com sucesso"
        )

    @staticmethod
    def update(content_id: str, data: dict, admin_id: str) -> Result[dict]:
        """
        Atualiza um conteudo.

        Args:
            content_id: ID do conteudo
            data: Dados para atualizar
            admin_id: ID do administrador

        Returns:
            Result contendo dados atualizados
        """
        # Get admin's class groups
        class_groups_stmt = select(ClassGroup.id).where(ClassGroup.admin_id == admin_id)

        stmt = select(ContentNode).where(
            ContentNode.id == content_id,
            ContentNode.class_group_id.in_(class_groups_stmt)
        )
        result = db.session.execute(stmt)
        node = result.scalar_one_or_none()

        if not node:
            return Result.fail(
                message="Conteudo nao encontrado",
                code="NOT_FOUND"
            )

        # If parent_id is provided, verify it exists
        if 'parent_id' in data and data['parent_id']:
            stmt = select(ContentNode).where(
                ContentNode.id == data['parent_id'],
                ContentNode.class_group_id == node.class_group_id,
                ContentNode.type == ContentType.FOLDER
            )
            result = db.session.execute(stmt)
            parent = result.scalar_one_or_none()

            if not parent:
                return Result.fail(
                    message="Pasta pai nao encontrada",
                    code="PARENT_NOT_FOUND",
                    field="parent_id"
                )

            # Prevent circular reference
            if str(data['parent_id']) == str(node.id):
                return Result.fail(
                    message="Conteudo nao pode ser pai de si mesmo",
                    code="CIRCULAR_REFERENCE",
                    field="parent_id"
                )

        # Update base fields
        if 'title' in data:
            node.title = data['title']
        if 'description' in data:
            node.description = data['description']
        if 'parent_id' in data:
            node.parent_id = data['parent_id'] if data['parent_id'] else None
        if 'order' in data:
            node.order = data['order']
        if 'visibility' in data:
            visibility_map = {
                'publico': ContentVisibility.PUBLIC,
                'privado': ContentVisibility.PRIVATE,
                'restrito': ContentVisibility.RESTRICTED
            }
            if data['visibility'] in visibility_map:
                node.visibility = visibility_map[data['visibility']]
        if 'meta_data' in data:
            node.meta_data = data['meta_data']

        node.updated_at = datetime.now(timezone.utc)

        # Update type-specific fields
        if isinstance(node, Folder):
            if 'color' in data:
                node.color = data['color']
            if 'icon' in data:
                node.icon = data['icon']
            if 'allow_upload' in data:
                node.allow_upload = data['allow_upload']
        elif isinstance(node, YouTubeLink):
            if 'duration' in data:
                node.duration = data['duration']
            if 'thumbnail_url' in data:
                node.thumbnail_url = data['thumbnail_url']
            if 'channel' in data:
                node.channel = data['channel']

        db.session.commit()

        return Result.success(
            value=ContentNodeService._serialize_content_node(node),
            message="Conteudo atualizado com sucesso"
        )

    @staticmethod
    def delete(content_id: str, admin_id: str) -> Result[None]:
        """
        Remove um conteudo.

        Args:
            content_id: ID do conteudo
            admin_id: ID do administrador

        Returns:
            Result indicando sucesso ou erro
        """
        # Get admin's class groups
        class_groups_stmt = select(ClassGroup.id).where(ClassGroup.admin_id == admin_id)

        stmt = select(ContentNode).where(
            ContentNode.id == content_id,
            ContentNode.class_group_id.in_(class_groups_stmt)
        )
        result = db.session.execute(stmt)
        node = result.scalar_one_or_none()

        if not node:
            return Result.fail(
                message="Conteudo nao encontrado",
                code="NOT_FOUND"
            )

        # Check if node is a folder with children
        if isinstance(node, Folder):
            stmt = select(ContentNode).where(ContentNode.parent_id == node.id)
            result = db.session.execute(stmt)
            children = result.scalars().first()

            if children:
                return Result.fail(
                    message="Nao e possivel excluir pasta com conteudos",
                    code="HAS_CHILDREN"
                )

        db.session.delete(node)
        db.session.commit()

        return Result.success(
            value=None,
            message="Conteudo removido com sucesso"
        )
