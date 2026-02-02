"""Controller para autenticacao da plataforma."""
from http import HTTPStatus

from apiflask import APIBlueprint

from resources.platform.auth.signin.service import SigninService
from resources.platform.auth.signin.schemas import SigninRequestSchema
from resources.platform.auth.signup.service import SignupService
from resources.platform.auth.signup.schemas import SignupRequestSchema
from utils.response import ApiResponse


auth_bp = APIBlueprint('platform_auth', __name__, url_prefix='/api/auth')


@auth_bp.post('/signin')
@auth_bp.input(SigninRequestSchema)
@auth_bp.doc(tags=['Platform Auth'], summary='Student sign in')
def signin(json_data):
    """
    Realiza login de estudante.

    Retorna tokens JWT para autenticacao em endpoints protegidos.
    """
    result = SigninService.signin(json_data)

    if result.is_failure:
        return ApiResponse.unauthorized(
            message=result.message
        ).to_tuple()

    return ApiResponse.ok(
        data=result.value,
        message=result.message
    ).to_tuple()


@auth_bp.post('/signup')
@auth_bp.input(SignupRequestSchema)
@auth_bp.doc(tags=['Platform Auth'], summary='Student sign up')
def signup(json_data):
    """
    Realiza cadastro de estudante.

    Cria novo estudante e retorna tokens JWT.
    """
    result = SignupService.signup(json_data)

    if result.is_failure:
        return ApiResponse.bad_request(
            message=result.message,
            errors=[{
                'code': result.code,
                'message': result.message,
                'field': result.field
            }]
        ).to_tuple()

    return ApiResponse.created(
        data=result.value,
        message=result.message
    ).to_tuple()
