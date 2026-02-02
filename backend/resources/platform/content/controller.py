"""Controller para conteudos da plataforma."""
from apiflask import APIBlueprint, Schema
from apiflask.fields import String

from resources.platform.content.service import StudentContentService
from utils.response import ApiResponse
from utils.auth import require_auth, get_current_user_id


content_bp = APIBlueprint('platform_content', __name__, url_prefix='/api/content')


class ContentQuerySchema(Schema):
    """Schema para query de conteudos."""
    parent_id = String(load_default=None)


@content_bp.get('/class/<class_group_id>')
@content_bp.input(ContentQuerySchema, location='query')
@require_auth
@content_bp.doc(tags=['Platform Content'], summary='List contents of a class group')
def list_contents(class_group_id, query_data):
    """Lista conteudos de uma turma."""
    student_id = get_current_user_id()
    parent_id = query_data.get('parent_id')

    result = StudentContentService.list_contents(
        student_id=student_id,
        class_group_id=class_group_id,
        parent_id=parent_id
    )

    if result.is_failure:
        if result.code == 'NOT_ENROLLED':
            return ApiResponse.forbidden(message=result.message).to_tuple()
        return ApiResponse.bad_request(message=result.message).to_tuple()

    return ApiResponse.ok(data=result.value).to_tuple()


@content_bp.get('/<content_id>')
@require_auth
@content_bp.doc(tags=['Platform Content'], summary='Get content details')
def get_content(content_id):
    """Obtem detalhes de um conteudo."""
    student_id = get_current_user_id()

    result = StudentContentService.get_content(
        student_id=student_id,
        content_id=content_id
    )

    if result.is_failure:
        if result.code == 'NOT_FOUND':
            return ApiResponse.not_found(message=result.message).to_tuple()
        if result.code in ['ACCESS_DENIED', 'PRIVATE_CONTENT']:
            return ApiResponse.forbidden(message=result.message).to_tuple()
        return ApiResponse.bad_request(message=result.message).to_tuple()

    return ApiResponse.ok(data=result.value).to_tuple()


@content_bp.get('/<content_id>/breadcrumbs')
@require_auth
@content_bp.doc(tags=['Platform Content'], summary='Get content breadcrumbs')
def get_breadcrumbs(content_id):
    """Obtem caminho de navegacao ate o conteudo."""
    student_id = get_current_user_id()

    result = StudentContentService.get_breadcrumbs(
        student_id=student_id,
        content_id=content_id
    )

    if result.is_failure:
        if result.code == 'NOT_FOUND':
            return ApiResponse.not_found(message=result.message).to_tuple()
        if result.code == 'ACCESS_DENIED':
            return ApiResponse.forbidden(message=result.message).to_tuple()
        return ApiResponse.bad_request(message=result.message).to_tuple()

    return ApiResponse.ok(data=result.value).to_tuple()
