"""Controller para cursos da plataforma."""
from apiflask import APIBlueprint

from resources.platform.courses.list.service import CoursesListService
from utils.response import ApiResponse
from utils.auth import require_auth, get_current_user_id


courses_bp = APIBlueprint('platform_courses', __name__, url_prefix='/api/courses')


@courses_bp.get('')
@require_auth
@courses_bp.doc(tags=['Platform Courses'], summary='List enrolled courses')
def list_courses():
    """Lista os cursos em que o estudante esta matriculado."""
    student_id = get_current_user_id()

    result = CoursesListService.list_courses(student_id)

    if result.is_failure:
        return ApiResponse.bad_request(message=result.message).to_tuple()

    return ApiResponse.ok(data=result.value).to_tuple()
