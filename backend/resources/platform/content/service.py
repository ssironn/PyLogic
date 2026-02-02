"""Servico de conteudos para estudantes."""
from typing import Optional

from sqlalchemy import select

from app.extensions import db
from models import ContentNode, ClassGroup, Enrollment, Folder, FileResource, YouTubeLink
from models.enums import ContentVisibility, EnrollmentStatus
from utils.response import Result


class StudentContentService:
    """Servico para acesso de conteudos por estudantes."""

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
            'created_at': node.created_at.isoformat() if node.created_at else None,
        }

        # Add type-specific fields
        if isinstance(node, Folder):
            base['color'] = node.color
            base['icon'] = node.icon
        elif isinstance(node, FileResource):
            base['drive_file_id'] = node.drive_file_id
            base['drive_url'] = node.drive_url
            base['original_name'] = node.original_name
            base['mime_type'] = node.mime_type
            base['size'] = node.size
        elif isinstance(node, YouTubeLink):
            base['youtube_id'] = node.youtube_id
            base['full_url'] = node.full_url
            base['duration'] = node.duration
            base['thumbnail_url'] = node.thumbnail_url
            base['channel'] = node.channel

        return base

    @staticmethod
    def _check_enrollment(student_id: str, class_group_id: str) -> bool:
        """Verifica se o estudante esta matriculado na turma."""
        stmt = select(Enrollment).where(
            Enrollment.student_id == student_id,
            Enrollment.class_group_id == class_group_id,
            Enrollment.status == EnrollmentStatus.ACTIVE
        )
        result = db.session.execute(stmt)
        return result.scalar_one_or_none() is not None

    @staticmethod
    def list_contents(
        student_id: str,
        class_group_id: str,
        parent_id: Optional[str] = None
    ) -> Result[list]:
        """
        Lista conteudos visiveis para o estudante.

        Args:
            student_id: ID do estudante
            class_group_id: ID da turma
            parent_id: ID da pasta pai (None para raiz)

        Returns:
            Result contendo lista de conteudos
        """
        # Verify enrollment
        if not StudentContentService._check_enrollment(student_id, class_group_id):
            return Result.fail(
                message="Voce nao esta matriculado nesta turma",
                code="NOT_ENROLLED"
            )

        # Build query - only public and restricted content (not private)
        stmt = select(ContentNode).where(
            ContentNode.class_group_id == class_group_id,
            ContentNode.visibility.in_([ContentVisibility.PUBLIC, ContentVisibility.RESTRICTED])
        )

        if parent_id:
            stmt = stmt.where(ContentNode.parent_id == parent_id)
        else:
            stmt = stmt.where(ContentNode.parent_id.is_(None))

        stmt = stmt.order_by(ContentNode.order, ContentNode.title)

        result = db.session.execute(stmt)
        nodes = result.scalars().all()

        return Result.success(
            value=[StudentContentService._serialize_content_node(node) for node in nodes]
        )

    @staticmethod
    def get_content(student_id: str, content_id: str) -> Result[dict]:
        """
        Obtem um conteudo especifico.

        Args:
            student_id: ID do estudante
            content_id: ID do conteudo

        Returns:
            Result contendo dados do conteudo
        """
        stmt = select(ContentNode).where(ContentNode.id == content_id)
        result = db.session.execute(stmt)
        node = result.scalar_one_or_none()

        if not node:
            return Result.fail(
                message="Conteudo nao encontrado",
                code="NOT_FOUND"
            )

        # Verify enrollment
        if not StudentContentService._check_enrollment(student_id, str(node.class_group_id)):
            return Result.fail(
                message="Voce nao tem acesso a este conteudo",
                code="ACCESS_DENIED"
            )

        # Check visibility
        if node.visibility == ContentVisibility.PRIVATE:
            return Result.fail(
                message="Este conteudo nao esta disponivel",
                code="PRIVATE_CONTENT"
            )

        return Result.success(
            value=StudentContentService._serialize_content_node(node)
        )

    @staticmethod
    def get_breadcrumbs(student_id: str, content_id: str) -> Result[list]:
        """
        Obtem o caminho de navegacao ate o conteudo.

        Args:
            student_id: ID do estudante
            content_id: ID do conteudo

        Returns:
            Result contendo lista de breadcrumbs
        """
        stmt = select(ContentNode).where(ContentNode.id == content_id)
        result = db.session.execute(stmt)
        node = result.scalar_one_or_none()

        if not node:
            return Result.fail(
                message="Conteudo nao encontrado",
                code="NOT_FOUND"
            )

        # Verify enrollment
        if not StudentContentService._check_enrollment(student_id, str(node.class_group_id)):
            return Result.fail(
                message="Voce nao tem acesso a este conteudo",
                code="ACCESS_DENIED"
            )

        # Build breadcrumbs
        breadcrumbs = []
        current = node

        while current:
            breadcrumbs.insert(0, {
                'id': str(current.id),
                'title': current.title,
                'type': current.type.value if current.type else None
            })

            if current.parent_id:
                stmt = select(ContentNode).where(ContentNode.id == current.parent_id)
                result = db.session.execute(stmt)
                current = result.scalar_one_or_none()
            else:
                break

        return Result.success(value=breadcrumbs)
