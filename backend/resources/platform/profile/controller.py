"""Controller para perfil da plataforma."""
from http import HTTPStatus

from apiflask import APIBlueprint

from resources.platform.profile.get.service import ProfileGetService
from resources.platform.profile.update.service import ProfileUpdateService
from resources.platform.profile.password.service import PasswordChangeService
from resources.platform.profile.schemas import (
    ProfileUpdateRequestSchema,
    PasswordChangeRequestSchema
)
from utils.response import ApiResponse
from utils.auth import require_auth, get_current_user_id


profile_bp = APIBlueprint('platform_profile', __name__, url_prefix='/api/profile')


@profile_bp.get('')
@require_auth
@profile_bp.doc(tags=['Platform Profile'], summary='Get student profile')
def get_profile():
    """Obtem o perfil do estudante autenticado."""
    student_id = get_current_user_id()

    result = ProfileGetService.get_profile(student_id)

    if result.is_failure:
        return ApiResponse.not_found(message=result.message).to_tuple()

    return ApiResponse.ok(data=result.value).to_tuple()


@profile_bp.put('')
@require_auth
@profile_bp.input(ProfileUpdateRequestSchema)
@profile_bp.doc(tags=['Platform Profile'], summary='Update student profile')
def update_profile(json_data):
    """Atualiza o perfil do estudante autenticado."""
    student_id = get_current_user_id()

    result = ProfileUpdateService.update_profile(student_id, json_data)

    if result.is_failure:
        if result.error and result.error.code == 'NOT_FOUND':
            return ApiResponse.not_found(message=result.message).to_tuple()
        return ApiResponse.bad_request(
            message=result.message,
            errors=[result.error] if result.error else None
        ).to_tuple()

    return ApiResponse.ok(
        data=result.value,
        message=result.message
    ).to_tuple()


@profile_bp.put('/password')
@require_auth
@profile_bp.input(PasswordChangeRequestSchema)
@profile_bp.doc(tags=['Platform Profile'], summary='Change password')
def change_password(json_data):
    """Altera a senha do estudante autenticado."""
    student_id = get_current_user_id()

    result = PasswordChangeService.change_password(student_id, json_data)

    if result.is_failure:
        return ApiResponse.bad_request(
            message=result.message,
            errors=[result.error] if result.error else None
        ).to_tuple()

    return ApiResponse.ok(message=result.message).to_tuple()
